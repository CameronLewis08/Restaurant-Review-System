SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users';

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'restaurants';

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'reviews';

SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'reviews';

SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'reviews';

SELECT trigger_name, event_manipulation, action_timing
FROM information_schema.triggers
WHERE event_object_table = 'reviews';