* =====================================================================
   Food Wastage Management System
   ===================================================================== */

CREATE DATABASE foodwastagedb;
 
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS food_listings;
DROP TABLE IF EXISTS providers;
DROP TABLE IF EXISTS receivers;
 
-- Providers table
CREATE TABLE providers (
    provider_id   INT PRIMARY KEY,
    name          VARCHAR(150),
    type          VARCHAR(100),
    address       VARCHAR(255),
    city          VARCHAR(100),
    contact       VARCHAR(100)
);
 
-- Receivers table
CREATE TABLE receivers (
    receiver_id   INT PRIMARY KEY,
    name          VARCHAR(150),
    type          VARCHAR(100),
    city          VARCHAR(100),
    contact       VARCHAR(100)
);
 
-- Food Listings table
CREATE TABLE food_listings (
    food_id        INT PRIMARY KEY,
    food_name      VARCHAR(150),
    quantity       INT,
    expiry_date    DATE,
    provider_id    INT,
    provider_type  VARCHAR(100),
    location       VARCHAR(100),
    food_type      VARCHAR(50),
    meal_type      VARCHAR(50),
    CONSTRAINT fk_foodlistings_providers
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
);
 
-- Claims table
CREATE TABLE claims (
    claim_id      INT PRIMARY KEY,
    food_id       INT,
    receiver_id   INT,
    status        VARCHAR(50),
    "timestamp"   TIMESTAMP,
    CONSTRAINT fk_claims_foodlistings
        FOREIGN KEY (food_id) REFERENCES food_listings(food_id),
    CONSTRAINT fk_claims_receivers
        FOREIGN KEY (receiver_id) REFERENCES receivers(receiver_id)
);
 
-- Quick check: tables should exist but be empty
SELECT 'providers' AS table_name, COUNT(*) AS row_count FROM providers
UNION ALL
SELECT 'receivers', COUNT(*) FROM receivers
UNION ALL
SELECT 'food_listings', COUNT(*) FROM food_listings
UNION ALL
SELECT 'claims', COUNT(*) FROM claims;

SELECT * FROM providers LIMIT 5;


Q1: Total food listed vs total food claimed
-- Shows overall system utilization
-- -----------------------------------------------------------------------
SELECT 
    (SELECT COUNT(*) FROM food_listings) AS total_food_listed,
    (SELECT COUNT(*) FROM claims) AS total_food_claimed,
    ROUND(
        (SELECT COUNT(*) FROM claims)::NUMERIC / 
        (SELECT COUNT(*) FROM food_listings) * 100, 2
    ) AS claim_rate_percent;
 
 
-- -----------------------------------------------------------------------
-- Q2: Top 10 providers by total quantity donated
-- -----------------------------------------------------------------------
SELECT 
    p.provider_id,
    p.name AS provider_name,
    p.type AS provider_type,
    p.city,
    SUM(fl.quantity) AS total_quantity_donated
FROM providers p
JOIN food_listings fl ON p.provider_id = fl.provider_id
GROUP BY p.provider_id, p.name, p.type, p.city
ORDER BY total_quantity_donated DESC
LIMIT 10;
 
 
-- -----------------------------------------------------------------------
-- Q3: Most claimed food types
-- -----------------------------------------------------------------------
SELECT 
    fl.food_type,
    COUNT(c.claim_id) AS total_claims
FROM food_listings fl
LEFT JOIN claims c ON fl.food_id = c.food_id
GROUP BY fl.food_type
ORDER BY total_claims DESC;
 
 
-- -----------------------------------------------------------------------
-- Q4: Claim status breakdown
-- -----------------------------------------------------------------------
SELECT 
    status,
    COUNT(*) AS total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM claims
GROUP BY status
ORDER BY total DESC;
 
 
-- -----------------------------------------------------------------------
-- Q5: City-wise food availability (total quantity per city)
-- -----------------------------------------------------------------------
SELECT 
    location AS city,
    COUNT(food_id) AS total_listings,
    SUM(quantity) AS total_quantity_available
FROM food_listings
GROUP BY location
ORDER BY total_quantity_available DESC;
 
 
-- -----------------------------------------------------------------------
-- Q6: Expiry analysis — expired vs not expired food
-- -----------------------------------------------------------------------
SELECT 
    CASE 
        WHEN expiry_date < CURRENT_DATE THEN 'Expired'
        WHEN expiry_date >= CURRENT_DATE AND expiry_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'Expiring Soon (7 days)'
        ELSE 'Fresh'
    END AS expiry_status,
    COUNT(*) AS total_items,
    SUM(quantity) AS total_quantity
FROM food_listings
WHERE expiry_date IS NOT NULL
GROUP BY expiry_status
ORDER BY total_items DESC;
 
 
-- -----------------------------------------------------------------------
-- Q7: Most active receivers (by number of claims)
-- -----------------------------------------------------------------------
SELECT 
    r.receiver_id,
    r.name AS receiver_name,
    r.type AS receiver_type,
    r.city,
    COUNT(c.claim_id) AS total_claims
FROM receivers r
JOIN claims c ON r.receiver_id = c.receiver_id
GROUP BY r.receiver_id, r.name, r.type, r.city
ORDER BY total_claims DESC
LIMIT 10;
 
 
-- -----------------------------------------------------------------------
-- Q8: Provider type breakdown (how many providers per type)
-- -----------------------------------------------------------------------
SELECT 
    type AS provider_type,
    COUNT(DISTINCT provider_id) AS total_providers,
    SUM(quantity) AS total_quantity_donated
FROM food_listings
GROUP BY type
ORDER BY total_quantity_donated DESC;
 
 
-- -----------------------------------------------------------------------
-- Q9: Monthly claim trends
-- -----------------------------------------------------------------------
SELECT 
    TO_CHAR("timestamp", 'YYYY-MM') AS month,
    COUNT(claim_id) AS total_claims
FROM claims
WHERE "timestamp" IS NOT NULL
GROUP BY TO_CHAR("timestamp", 'YYYY-MM')
ORDER BY month;
 
 
-- -----------------------------------------------------------------------
-- Q10: Food wastage rate — listings never claimed
-- -----------------------------------------------------------------------
SELECT 
    fl.food_id,
    fl.food_name,
    fl.quantity,
    fl.food_type,
    fl.location,
    fl.expiry_date
FROM food_listings fl
LEFT JOIN claims c ON fl.food_id = c.food_id
WHERE c.claim_id IS NULL
ORDER BY fl.expiry_date ASC;
 
 
-- -----------------------------------------------------------------------
-- Q11: Meal type distribution
-- -----------------------------------------------------------------------
SELECT 
    meal_type,
    COUNT(*) AS total_listings,
    SUM(quantity) AS total_quantity,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM food_listings
GROUP BY meal_type
ORDER BY total_listings DESC;
 
 
-- -----------------------------------------------------------------------
-- Q12: Average quantity donated per provider type
-- -----------------------------------------------------------------------
SELECT 
    p.type AS provider_type,
    ROUND(AVG(fl.quantity), 2) AS avg_quantity_per_listing,
    SUM(fl.quantity) AS total_quantity,
    COUNT(fl.food_id) AS total_listings
FROM providers p
JOIN food_listings fl ON p.provider_id = fl.provider_id
GROUP BY p.type
ORDER BY avg_quantity_per_listing DESC;
 
 
-- -----------------------------------------------------------------------
-- Q13: Receivers by city
-- -----------------------------------------------------------------------
SELECT 
    city,
    COUNT(receiver_id) AS total_receivers,
    COUNT(DISTINCT type) AS receiver_types
FROM receivers
GROUP BY city
ORDER BY total_receivers DESC;
 
 
-- -----------------------------------------------------------------------
-- Q14: Top 10 food items with highest wastage (unclaimed quantity)
-- -----------------------------------------------------------------------
SELECT 
    fl.food_name,
    fl.food_type,
    SUM(fl.quantity) AS total_quantity_listed,
    COUNT(c.claim_id) AS times_claimed,
    SUM(fl.quantity) - COUNT(c.claim_id) AS wasted_quantity
FROM food_listings fl
LEFT JOIN claims c ON fl.food_id = c.food_id
GROUP BY fl.food_name, fl.food_type
ORDER BY wasted_quantity DESC
LIMIT 10;
 
 
-- -----------------------------------------------------------------------
-- Q15: Claim success rate by food type
-- -----------------------------------------------------------------------
SELECT 
    fl.food_type,
    COUNT(fl.food_id) AS total_listed,
    COUNT(c.claim_id) AS total_claimed,
    ROUND(COUNT(c.claim_id) * 100.0 / NULLIF(COUNT(fl.food_id), 0), 2) AS claim_success_rate
FROM food_listings fl
LEFT JOIN claims c ON fl.food_id = c.food_id
GROUP BY fl.food_type
ORDER BY claim_success_rate DESC;
 
 
-- -----------------------------------------------------------------------
-- Q16: Providers with zero claims (inactive providers)
-- -----------------------------------------------------------------------
SELECT 
    p.provider_id,
    p.name,
    p.type,
    p.city,
    COUNT(fl.food_id) AS total_listings
FROM providers p
LEFT JOIN food_listings fl ON p.provider_id = fl.provider_id
LEFT JOIN claims c ON fl.food_id = c.food_id
WHERE c.claim_id IS NULL
GROUP BY p.provider_id, p.name, p.type, p.city
ORDER BY total_listings DESC;
 
 
-- -----------------------------------------------------------------------
-- Q17: Daily average claims
-- -----------------------------------------------------------------------
SELECT 
    ROUND(AVG(daily_claims), 2) AS avg_daily_claims
FROM (
    SELECT 
        DATE("timestamp") AS claim_date,
        COUNT(*) AS daily_claims
    FROM claims
    WHERE "timestamp" IS NOT NULL
    GROUP BY DATE("timestamp")
) daily;
 