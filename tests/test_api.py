from fastapi.testclient import TestClient
from app.main import app
def test_overview():
    with TestClient(app) as c:
        data=c.get('/api/overview').json(); assert data['cards']['revenue'] > 0 and len(data['trend']) == 30
def test_kpi_is_allowlisted():
    with TestClient(app) as c:
        assert c.post('/api/kpis',json={'metric':'revenue','start_date':'2027-01-01','end_date':'2027-01-31'}).status_code == 200
        assert c.post('/api/kpis',json={'metric':'DROP TABLE','start_date':'2027-01-01','end_date':'2027-01-31'}).status_code == 422
def test_rag_citations():
    with TestClient(app) as c:
        data=c.post('/api/ask',json={'question':'What happens when response time exceeds target?'}).json(); assert data['citations'] and data['citations'][0]['version']
def test_metric_question_uses_governed_tool():
    with TestClient(app) as c:
        data=c.post('/api/ask',json={'question':'What was revenue in the last 30 days?'}).json()
        assert data['trace']['tools'][0]['name'] == 'governed_kpi_query' and '$' in data['answer']
def test_retrieval_excludes_superseded_documents():
    with TestClient(app) as c:
        data=c.post('/api/ask',json={'question':'What is the response time target?'}).json()
        assert all(c['id'] != 'ops-playbook-v2' for c in data['citations'])
