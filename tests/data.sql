INSERT INTO
    Users (username, email, password, created)
VALUES
    (
        'test',
        'test@test.com',
        'scrypt:32768:8:1$5JFUp7hZJNWjYdRs$fd0b40414edf428a2f04ed418c7e0913768fcba509f6f0f77d6623419726eedffa783bd10516e6376ac4484eee6b2ea67d1f1a2608cef11f1df353893f495385',
        '2024-02-06 21:18:19'
    ),
    (
        'foo',
        'foo@bar.org',
        'scrypt:32768:8:1$SjMyoQ8KyiWU5Tmf$587f80846bd9f3aa05b4f227ee6be7e4d3f59f0f0e019bb68ac42cde132821c1ebf7fd2320966b3c55e1fe04a096fb6eda672b17652c96212939d94765d05b29',
        '2024-02-06 21:22:03'
    );

INSERT INTO
    Projects (owner, name, category, description, created)
VALUES
    (
        1,
        'Existing Project',
        0,
        'This is an existing test project.',
        '2024-02-06 21:18:19'
    ),
    (
        1,
        'The Other Existing Project',
        0,
        'This is another existing test project.',
        '2024-02-06 21:18:19'
    ),
    (
        2,
        'Another Test Project',
        0,
        'This is a project from another user.',
        '2024-02-06 21:22:03'
    );