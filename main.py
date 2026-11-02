def main():
    testes = {
        ("evt_001", "txn_001"): "test",
        ("evt_002", "txn_002"): "test2",
        "evt_003": "test3",
    }
    print(testes.get(("evt_001")))


if __name__ == "__main__":
    main()
