from api_validator import APIValidator

validator = APIValidator(
    tier='professional',
    license_key='PRO-2026-12-31-TEST-0001'
)

test_data = {
    'auth_token_present': True,
    'auth_token_valid_length': True,
    'user_verified': True,
    'requests_per_minute': 30,
    'requests_per_hour': 1000,
    'daily_requests': 5000,
    'payload_size_kb': 1024,
    'ip_reputation_score': 75,
    'failed_attempts': 0
}

result = validator.validate_request(test_data)
print(f"Score: {result.score:.3f}")
print(f"Valid: {result.is_valid}")

# Ver métricas (solo Professional/Enterprise)
metrics = validator.get_metrics()
print(f"Metrics: {metrics}")