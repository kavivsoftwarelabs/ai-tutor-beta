-- scripts/seed_postgres.sql

-- 1. DROP TABLES IF TESTING LOCALLY
DROP TABLE IF EXISTS student_knowledge_states CASCADE;
DROP TABLE IF EXISTS user_daily_constraints CASCADE;
DROP TABLE IF EXISTS curated_resources CASCADE;
DROP TABLE IF EXISTS concepts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 2. CREATE SYSTEM CORE TABLES
CREATE TABLE concepts (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    prerequisites JSONB DEFAULT '[]',     -- Stored as JSON array string: ["math_pct"]
    exam_importance REAL DEFAULT 0.15      -- Exam weight distribution score factor
);

CREATE TABLE curated_resources (
    id SERIAL PRIMARY KEY,
    concept_id VARCHAR(100) REFERENCES concepts(id) ON DELETE CASCADE,
    video_id VARCHAR(11) NOT NULL,
    start_time_seconds INT NOT NULL,
    end_time_seconds INT NOT NULL,
    title VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_daily_constraints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    available_minutes INT NOT NULL,
    UNIQUE(user_id, date)
);

CREATE TABLE student_knowledge_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    concept_id VARCHAR(100) REFERENCES concepts(id) ON DELETE CASCADE,
    mastery_score REAL NOT NULL DEFAULT 50.0,      -- Range: 0.0 to 100.0 (Starting baseline)
    review_due_factor REAL NOT NULL DEFAULT 0.0,   -- Range: 0.0 (Fresh) to 1.0 (Overdue)
    attempt_count INT DEFAULT 0,
    consecutive_correct INT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, concept_id)
);

-- 3. SEED INITIAL FOUNDATIONAL SPREAD (CUET General Aptitude Matrix)
INSERT INTO concepts (id, name, prerequisites, exam_importance) VALUES
('math_pct', 'Percentages & Fractions', '[]', 0.15),
('math_pl', 'Profit and Loss', '["math_pct"]', 0.15),
('math_ratio', 'Ratio and Proportion', '[]', 0.12),
('math_si', 'Simple Interest', '["math_pct", "math_ratio"]', 0.10),
('math_ci', 'Compound Interest', '["math_si"]', 0.10);
