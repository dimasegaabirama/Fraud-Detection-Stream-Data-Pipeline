
INSERT INTO transaction_events (
    event_id, transaction_id, user_id, amount, currency, segment,
    transaction_type, direction, sender_account, receiver_account, merchant_id,
    ip_address, device_id, device_type, latitude, longitude, status, event_timestamp
) VALUES
-- Aktivitas normal (Jakarta)
('evt-0001', 'txn-1001', 'usr-001',    150000.00, 'IDR', 'retail',     'transfer',   'out', 'ACC-1001-0001', 'ACC-2002-0042', NULL,           '103.28.12.45',  'dev-a1', 'android', '-6.2088',  '106.8456', 'success',  '2026-11-20T02:15:10Z'),
('evt-0002', 'txn-1002', 'usr-001',     45000.00, 'IDR', 'retail',     'payment',    'out', 'ACC-1001-0001', NULL,            'mch-warung01', '103.28.12.45',  'dev-a1', 'android', '-6.2090',  '106.8460', 'success',  '2026-11-20T05:40:22Z'),
('evt-0003', 'txn-1003', 'usr-001',   2500000.00, 'IDR', 'retail',     'top_up',     'in',  NULL,            'ACC-1001-0001', NULL,           '103.28.12.45',  'dev-a1', 'android', '-6.2088',  '106.8456', 'success',  '2026-11-21T01:00:00Z'),
('evt-0004', 'txn-1004', 'usr-002',    500000.00, 'IDR', 'retail',     'withdrawal', 'out', 'ACC-1002-0007', NULL,            NULL,           '114.122.5.9',   'dev-b1', 'ios',     '-6.1751',  '106.8650', 'success',  '2026-11-21T08:30:45Z'),
('evt-0005', 'txn-1005', 'usr-002',     89900.00, 'IDR', 'retail',     'payment',    'out', 'ACC-1002-0007', NULL,            'mch-tokoku',   '114.122.5.9',   'dev-b1', 'ios',     '-6.1751',  '106.8650', 'success',  '2026-11-21T10:05:00Z'),

-- Segment individual
('evt-0006', 'txn-1006', 'usr-003',     12500.00, 'USD', 'individual', 'transfer',   'out', 'ACC-3003-0100', 'ACC-9009-0500', NULL,           '202.58.100.21', 'dev-c1', 'web',     '1.3521',   '103.8198', 'success',  '2026-11-22T03:12:00Z'),
('evt-0007', 'txn-1007', 'usr-003',      3200.50, 'USD', 'individual', 'payment',    'out', 'ACC-3003-0100', NULL,            'mch-luxhotel', '202.58.100.21', 'dev-c1', 'web',     '1.3521',   '103.8198', 'success',  '2026-11-22T03:45:30Z'),
('evt-0008', 'txn-1008', 'usr-004',     75000.00, 'EUR', 'individual', 'top_up',     'in',  NULL,            'ACC-4004-0222', NULL,           '81.2.69.142',   'dev-d1', 'ios',     '51.5074',  '-0.1278',  'success',  '2026-11-22T09:00:00Z'),

-- Segment business
('evt-0009', 'txn-1009', 'usr-005',    250000.00, 'USD', 'business',   'transfer',   'out', 'ACC-5005-0900', 'ACC-8008-0111', NULL,           '66.249.64.10',  'dev-e1', 'web',     '40.7128',  '-74.0060', 'success',  '2026-11-23T14:20:00Z'),
('evt-0010', 'txn-1010', 'usr-005',    980000.00, 'USD', 'business',   'transfer',   'out', 'ACC-5005-0900', 'ACC-8008-0112', NULL,           '66.249.64.10',  'dev-e1', 'web',     '40.7128',  '-74.0060', 'reserved', '2026-11-23T14:25:00Z'),
('evt-0011', 'txn-1011', 'usr-006',      1800.00, 'GBP', 'business',   'payment',    'out', 'ACC-6006-0333', NULL,            'mch-officeco', '51.140.22.8',   'dev-f1', 'web',     '51.5074',  '-0.1278',  'success',  '2026-11-23T11:10:00Z'),
('evt-0012', 'txn-1012', 'usr-006',      1800.00, 'GBP', 'business',   'refund',     'in',  NULL,            'ACC-6006-0333', 'mch-officeco', '51.140.22.8',   'dev-f1', 'web',     '51.5074',  '-0.1278',  'success',  '2026-11-24T09:30:00Z'),

-- Pola mencurigakan 1: velocity / transfer kecil berturut-turut (usr-007, device sama)
('evt-0013', 'txn-1013', 'usr-007',      9990.00, 'USD', 'retail',     'transfer',   'out', 'ACC-7007-0001', 'ACC-9999-0001', NULL,           '185.220.101.5', 'dev-x1', 'android', '55.7558',  '37.6173',  'success',  '2026-11-24T22:01:00Z'),
('evt-0014', 'txn-1014', 'usr-007',      9990.00, 'USD', 'retail',     'transfer',   'out', 'ACC-7007-0001', 'ACC-9999-0002', NULL,           '185.220.101.5', 'dev-x1', 'android', '55.7558',  '37.6173',  'success',  '2026-11-24T22:03:00Z'),
('evt-0015', 'txn-1015', 'usr-007',      9990.00, 'USD', 'retail',     'transfer',   'out', 'ACC-7007-0001', 'ACC-9999-0003', NULL,           '185.220.101.5', 'dev-x1', 'android', '55.7558',  '37.6173',  'success',  '2026-11-24T22:05:00Z'),
('evt-0016', 'txn-1016', 'usr-007',      9990.00, 'USD', 'retail',     'transfer',   'out', 'ACC-7007-0001', 'ACC-9999-0004', NULL,           '185.220.101.5', 'dev-x1', 'android', '55.7558',  '37.6173',  'failed',   '2026-11-24T22:07:00Z'),

-- Pola mencurigakan 2: satu device dipakai beberapa user berbeda
('evt-0017', 'txn-1017', 'usr-008',      2000.00, 'USD', 'retail',     'cashout',    'out', 'ACC-8008-0777', NULL,            NULL,           '45.13.22.90',   'dev-x1', 'android', '55.7558',  '37.6173',  'success',  '2026-11-24T23:15:00Z'),
('evt-0018', 'txn-1018', 'usr-009',      1500.00, 'USD', 'retail',     'payment',    'out', 'ACC-9009-0888', NULL,            'mch-cryptox',  '45.13.22.90',   'dev-x1', 'android', '55.7558',  '37.6173',  'failed',   '2026-11-24T23:20:00Z'),

-- Pola mencurigakan 3: impossible travel (usr-001: Jakarta -> New York dalam 30 menit)
('evt-0019', 'txn-1019', 'usr-001',    750000.00, 'IDR', 'retail',     'payment',    'out', 'ACC-1001-0001', NULL,            'mch-electro9', '198.51.100.77', 'dev-z9', 'web',     '40.7128',  '-74.0060', 'success',  '2026-11-25T01:00:00Z'),
('evt-0020', 'txn-1020', 'usr-001',    300000.00, 'IDR', 'retail',     'transfer',   'out', 'ACC-1001-0001', 'ACC-2002-0042', NULL,           '103.28.12.45',  'dev-a1', 'android', '-6.2088',  '106.8456', 'success',  '2026-11-25T01:30:00Z');
