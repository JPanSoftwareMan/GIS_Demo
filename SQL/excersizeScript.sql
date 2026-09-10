-- Create a working copy of the backup table
CREATE TABLE meat_poultry_egg_establishments AS
SELECT *
FROM meat_poultry_egg_establishments_bk;

-- Add a boolean field to indicate whether an establishment performs meat processing
ALTER TABLE meat_poultry_egg_establishments
ADD COLUMN meat_processing BOOLEAN;

-- Add a boolean field to indicate whether an establishment performs poultry processing
ALTER TABLE meat_poultry_egg_establishments
ADD COLUMN poultry_processing BOOLEAN;

-- Review the table structure and data
SELECT *
FROM meat_poultry_egg_establishments;

-- Set meat_processing to TRUE when the Activities field contains "Meat Processing"
UPDATE meat_poultry_egg_establishments
SET meat_processing = TRUE
WHERE activities ILIKE '%Meat Processing%';

-- Set poultry_processing to TRUE when the Activities field contains "Poultry Processing"
UPDATE meat_poultry_egg_establishments
SET poultry_processing = TRUE
WHERE activities ILIKE '%Poultry Processing%';

-- Add a field to identify establishments that perform both meat and poultry processing
ALTER TABLE meat_poultry_egg_establishments
ADD COLUMN meat_and_poultry_processing BOOLEAN;

-- Set meat_and_poultry_processing to TRUE when both processing flags are TRUE
UPDATE meat_poultry_egg_establishments
SET meat_and_poultry_processing = TRUE
WHERE poultry_processing = TRUE
  AND meat_processing = TRUE;

-- View all establishments that perform both meat and poultry processing
SELECT *
FROM meat_poultry_egg_establishments
WHERE poultry_processing = TRUE
  AND meat_processing = TRUE;

-- Generate a summary count of establishments by processing type
SELECT
    meat_processing,
    poultry_processing,
    COUNT(*) AS establishment_count
FROM meat_poultry_egg_establishments
GROUP BY meat_processing, poultry_processing
ORDER BY meat_processing, poultry_processing;

-- Alternative query to find establishments that perform both meat and poultry processing
-- (IS TRUE explicitly handles boolean values)
SELECT *
FROM meat_poultry_egg_establishments
WHERE poultry_processing = TRUE
  AND meat_processing IS TRUE;