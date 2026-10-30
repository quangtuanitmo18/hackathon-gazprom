"""Candidate ranking is non-authoritative, tenant-local and label-blind."""
from productpulse.data.canonical import CanonicalTicketV1, ticket_key
from productpulse.incident.candidates import rank_review_candidates

def ticket(id_, text, *, product="erp", component="auth", error=("HTTP 403",)):
    return CanonicalTicketV1(
        source_system="fixture",source_ticket_id=id_,provenance_id="synthetic",
        body_redacted=text,product_id=product,component_id=component,
        reported_version="2.1",error_codes=error,
    )

def inputs(*items):
    return [(ticket_key(t),t,p) for t,p in items]

def test_russian_recurrent_failures_rank_ahead_of_unrelated_tickets():
    a=ticket("a","Сбой авторизации ERP HTTP 403 после обновления")
    b=ticket("b","После обновления ошибка авторизации ERP HTTP 403")
    c=ticket("c","Доставка и бухгалтерские документы PDF",product="docs",component="print",error=())
    out=rank_review_candidates(inputs((a,"PRB-1"),(b,"PRB-2"),(c,"PRB-3")))
    assert out
    assert out[0]["ticket_key_a"]==min(ticket_key(a),ticket_key(b))
    assert out[0]["ticket_key_b"]==max(ticket_key(a),ticket_key(b))
    assert "lexical_overlap" in out[0]["signals"]
    assert "shared_error_code" in out[0]["signals"]
    assert "same_component" in out[0]["signals"]
    assert "same_product" in out[0]["signals"]
    assert out[0]["rank"]>=1
    assert "confidence" not in out[0] and "is_duplicate" not in out[0]

def test_candidate_pairs_are_undirected_unique_and_stable_under_input_order():
    a=ticket("a","Сбой авторизации HTTP 403 в ERP")
    b=ticket("b","Сбой авторизации HTTP 403 ERP")
    c=ticket("c","Сбой авторизации HTTP 403 ERP сегодня")
    values=inputs((a,"p1"),(b,"p2"),(c,"p3"))
    results=rank_review_candidates(values)
    keys=[(x["ticket_key_a"],x["ticket_key_b"]) for x in results]
    assert len(keys)==len(set(keys))
    assert all(a!=b for a,b in keys)
    assert results==rank_review_candidates(list(reversed(values)))

def test_same_active_problem_and_confirmed_approval_excluded():
    a=ticket("a","Одна ошибка HTTP 403 ERP")
    b=ticket("b","Ошибка HTTP 403 ERP авторизация")
    common=inputs((a,"same"),(b,"same"))
    assert rank_review_candidates(common)==()
    pairs=inputs((a,"p1"),(b,"p2"))
    pair_id=tuple(sorted((ticket_key(a),ticket_key(b))))
    assert rank_review_candidates(pairs,approved_pairs={pair_id})==()

def test_no_lexical_overlap_does_not_fabricate_suggestions():
    a=ticket("a","авторизация сломалась",error=())
    b=ticket("b","фактура распечатать",product="pdf",component="print",error=())
    assert rank_review_candidates(inputs((a,"a"),(b,"b")))==()

def test_corpus_cap_enforced_not_silently_truncated():
    tickets=[ticket(str(i),"Ошибка HTTP 403 система") for i in range(4)]
    try:
        rank_review_candidates(inputs(*[(t,str(i)) for i,t in enumerate(tickets)]),corpus_cap=3)
    except ValueError as exc:
        assert "capacity" in str(exc)
    else:
        raise AssertionError("must fail closed rather than silently rank first 3")

def test_rank_limit_and_bad_parameters():
    a=ticket("a","Ошибка HTTP 403 ERP")
    b=ticket("b","Ошибка HTTP 403 ERP")
    c=ticket("c","Ошибка HTTP 403 ERP")
    result=rank_review_candidates(inputs((a,"a"),(b,"b"),(c,"c")),limit=1)
    assert len(result)==1
    try:rank_review_candidates(inputs((a,"a"),(b,"b")),limit=0)
    except ValueError:pass
    else:raise AssertionError("invalid limit accepted")

def test_singleton_and_nonmatching_source_scoped_ticket_ids():
    a=ticket("same","Вход сломан HTTP 403")
    b=CanonicalTicketV1(source_system="different",source_ticket_id="same",provenance_id="synthetic",
                         body_redacted="Вход сломан HTTP 403")
    assert ticket_key(a)!=ticket_key(b)
    results=rank_review_candidates(inputs((a,"p1"),(b,"p2")))
    assert len(results)==1
