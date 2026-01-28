CREATE TABLE IF NOT EXISTS shared.ai_cases (
    id UUID PRIMARY KEY,
    case_id VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL,
    approved BOOLEAN NOT NULL,
    needs_human_approval BOOLEAN NOT NULL,
    risk_score INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL
);