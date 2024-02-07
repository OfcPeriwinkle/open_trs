INSERT INTO
    Users (username, email, password, created)
VALUES
    (
        'test',
        'test@firsttest.com',
        'scrypt:32768:8:1$KohBHT8qAHj9TZbG$dbeaf604b2d9748ce8a6d19dc9ab10762238f218e2bfd28cde45c741d3df380ce016751d2bca626c05158929285971dfeda04ca863c5cc64a12b5d1b4dd20fe6',
        '2024-02-06 21:18:19'
    ),
    (
        'foo',
        'foo@bar.org',
        'scrypt:32768:8:1$SjMyoQ8KyiWU5Tmf$587f80846bd9f3aa05b4f227ee6be7e4d3f59f0f0e019bb68ac42cde132821c1ebf7fd2320966b3c55e1fe04a096fb6eda672b17652c96212939d94765d05b29',
        '2024-02-06 21:22:03'
    );