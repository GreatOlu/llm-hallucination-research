"""Five-question pilot. Default is a free plan; --execute permits API calls."""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

from src.experiments.prompts import CONDITIONS, build_prompt

ROOT = Path(__file__).resolve().parents[2]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def save(path, state):
    """Replace the checkpoint atomically, after flushing it to disk."""
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(state, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(path):
    # Kernel releases this lock even after a crash. Do not delete the lock file.
    with open(str(path) + '.lock', 'a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another runner is using this output file.') from None
        yield


def configuration(root):
    paths = [root / 'data/processed' / name for name in (
        'answerable_questions.json', 'unanswerable_questions.json', 'knowledge_base.json')]
    answerable, unanswerable, corpus = [json.loads(p.read_text()) for p in paths]
    if len(answerable) < 3 or len(unanswerable) < 2:
        raise ValueError('Pilot requires at least three answerable and two screened unanswerable questions.')
    questions = []
    for group, items in [('answerable', answerable[:3]), ('unanswerable', unanswerable[:2])]:
        for q in items:
            if group == 'unanswerable' and q.get('screening_status') != 'pass':
                raise ValueError('Unanswerable question has not passed screening.')
            questions.append({'id': q['id'], 'question': q['question'],
                              'group': group, 'reference_answers': q['answers']['text']})
    if len({q['id'] for q in questions}) != 5:
        raise ValueError('Question IDs must be unique.')
    # Fingerprint all relevant source bytes without importing the API client.
    sources = paths + [root / 'src' / name for name in (
        'experiments/prompts.py', 'experiments/llm_client.py',
        'retrieval/hybrid_search.py', 'retrieval/semantic_search.py', 'retrieval/bm25_search.py')]
    return {'schema_version': 1, 'questions': questions, 'conditions': CONDITIONS,
            'retriever': {'name': 'HybridRetriever', 'top_k': 5, 'rrf_k': 60, 'candidate_k': 10},
            'max_output_tokens': 1000,
            'source_hashes': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}


def prepare(config, retriever, model):
    records = []
    for q in config['questions']:
        passages = retriever.retrieve(q['question'], top_k=5)
        if len(passages) != 5 or len({p['document_id'] for p in passages}) != 5:
            raise ValueError('HybridRetriever must return five distinct passages.')
        for condition in CONDITIONS:
            evidence = passages if condition.startswith('rag') else []
            records.append({'question_id': q['id'], 'question': q['question'],
                'group': q['group'], 'reference_answers': q['reference_answers'],
                'condition': condition, 'model': model,
                'prompt': build_prompt(q['question'], condition, evidence),
                'retrieved_document_ids': [p['document_id'] for p in evidence],
                'retrieved_passages': evidence, 'status': 'pending', 'answer': None,
                'input_tokens': None, 'output_tokens': None, 'error': None})
    return {'config': config, 'config_hash': digest(config), 'model': model, 'records': records}


def run(state, path, generate, max_calls):
    calls = 0
    for record in state['records']:
        if record['status'] != 'pending':
            continue
        if calls >= max_calls:
            break
        record.update(status='in_flight', started_at=datetime.now(timezone.utc).isoformat())
        save(path, state)  # Persist intent BEFORE a potentially billable request.
        calls += 1
        try:
            result = generate(record['prompt'])
            record.update({k: result[k] for k in ('answer', 'input_tokens', 'output_tokens')})
            record['response_model'] = result.get('model', record['model'])
            record['response_id'] = result.get('response_id')
            record['response_status'] = result.get('response_status')
            record['reasoning_tokens'] = result.get('reasoning_tokens')
            record['incomplete_reason'] = result.get('incomplete_reason')
            record['status'] = 'completed' if record['answer'].strip() else 'empty_response'
            if result.get('response_status') == 'incomplete':
                record['status'] = 'incomplete'
                record['error'] = {'type': 'IncompleteResponse', 'message': 'Response incomplete; inspect incomplete_reason and token usage.'}
            if record['status'] == 'empty_response':
                record['error'] = {'type': 'EmptyResponse', 'message': 'No answer text; inspect response status and token usage.'}
        except Exception as error:
            # Raw exception strings can contain credentials or request payloads.
            record.update(status='error', error={'type': type(error).__name__,
                'message': 'Request failed; not retried automatically. Billing outcome may be uncertain.'})
        record['finished_at'] = datetime.now(timezone.utc).isoformat()
        save(path, state)
        if record['status'] != 'completed':
            break  # Avoid spending the rest of the pilot on a persistent failure.
    return calls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Allow paid requests (default: free plan only).')
    parser.add_argument('--output', type=Path, default=ROOT / 'results/experiments/pilot_v2.json',
                        help='Checkpoint path (default: results/experiments/pilot_v2.json).')
    parser.add_argument('--max-calls', type=int, default=20, help='Request ceiling for this invocation, 0–20.')
    args = parser.parse_args()
    if not 0 <= args.max_calls <= 20:
        parser.error('--max-calls must be between 0 and 20')
    try:
        config = configuration(ROOT)
        if not args.execute:
            print('Free plan: 3 answerable + 2 screened unanswerable questions; 4 conditions; at most 20 requests.')
            print('HybridRetriever top_k=5; 1,000 output tokens/request (at most 20,000 output tokens).')
            print('Input tokens are additional. No dollar estimate is assumed. No API client or retriever loaded.')
            if args.output.exists():
                state = json.loads(args.output.read_text())
                if state['config_hash'] != digest(config):
                    raise ValueError('Source/configuration changed. Use a new output file for a new experiment.')
                print('Saved statuses:', dict(Counter(r['status'] for r in state['records'])))
            print('Output:', args.output)
            return
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with locked(args.output):
            if args.output.exists():
                state = json.loads(args.output.read_text())
                if state['config_hash'] != digest(config):
                    raise ValueError('Source/configuration changed. Use a new output file for a new experiment.')
            else:
                from src.experiments.llm_client import MODEL
                from src.retrieval.hybrid_search import HybridRetriever
                state = prepare(config, HybridRetriever(rrf_k=60, candidate_k=10), MODEL)
                save(args.output, state)
            if args.max_calls and any(r['status'] == 'pending' for r in state['records']):
                from src.experiments.llm_client import generate_response
                run(state, args.output, generate_response, args.max_calls)
            print('Saved statuses:', dict(Counter(r['status'] for r in state['records'])))
            print('Recorded tokens:', {k: sum(r[k] or 0 for r in state['records']) for k in ('input_tokens', 'output_tokens')})
            print('Output:', args.output)
            if any(r['status'] in ('error', 'in_flight', 'empty_response', 'incomplete') for r in state['records']):
                print('Some attempts need manual review; they will never be retried automatically.')
                return 1
    except Exception as error:
        # Do not print arbitrary exceptions from client initialization or retrieval.
        print('Pilot stopped:', type(error).__name__)
        if isinstance(error, ValueError):
            print(str(error))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
