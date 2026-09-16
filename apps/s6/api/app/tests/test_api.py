import json

def test_api_icono_index(client):
    response = client.get("/api/iconographie")
    
    assert response.status_code == 200

    response_parsed = json.loads(response.data)
    assert type(response_parsed) == list


def test_api_icono_main_ok(app, db, client):
    # NOTE: iconographie/1 is defined by the fixture `set_base_icono`
    response = client.get("/api/iconographie/1")
    
    assert response.status_code == 200

    response_parsed = json.loads(response.data)
    assert type(response_parsed) == dict


def test_api_icono_main_err(client):
    # cet ID n'existe pas => on devrait avoir une 404
    response = client.get("/api/iconographie/9999999")
    assert response.status_code == 404
