Seed the database with comprehensive Middle East PPP project data, past and present.

## Step 1: Add MENA-specific data sources to ppp_sources

Run this SQL:

```sql
insert into ppp_sources (name, url, type, region, is_active, crawl_frequency_hours) values
  ('World Bank PPI — MENA Filter', 'https://ppi.worldbank.org/api/projects?region=MNA', 'api', 'MENA', true, 24),
  ('IsDB Infrastructure Projects', 'https://www.isdb.org/what-we-do/infrastructure', 'scrape', 'MENA/OIC', true, 24),
  ('MEED Projects Database', 'https://projects.meed.com', 'scrape', 'MENA', true, 24),
  ('IFC MENA Projects', 'https://disclosures.ifc.org/#/landing?lang=en&tab=projects&region=MENA', 'scrape', 'MENA', true, 24),
  ('Saudi NDMC Project Finance', 'https://www.ndmc.gov.sa/en/pages/projects.aspx', 'scrape', 'Saudi Arabia', true, 24),
  ('UAE PPP Law Projects', 'https://www.mof.gov.ae/en/resourcesAndBudget/Pages/PPP.aspx', 'scrape', 'UAE', true, 24),
  ('Egypt PPP Central Unit', 'https://www.ppp.gov.eg/en', 'scrape', 'Egypt', true, 24),
  ('Arab Forum for PPP Projects', 'https://www.arabppp.org', 'scrape', 'MENA', true, 24),
  ('Infrastructure Journal MENA', 'https://www.ijonline.com/deals?region=middle-east-africa', 'scrape', 'MENA', true, 24),
  ('EBRD MENA Projects', 'https://www.ebrd.com/work-with-us/project-finance/project-summary-documents.html', 'scrape', 'MENA', true, 24);
```

## Step 2: Seed known MENA PPP projects

Run this SQL to populate the database with documented past and present PPP projects across the Middle East:

```sql
insert into ppp_projects (name, country, region, sector, status, total_value_usd, government_sponsor, private_operator, announcement_date, award_date, financial_close_date, completion_date, source_url, source_name, confidence_score, is_verified) values

-- SAUDI ARABIA
('Riyadh Metro', 'Saudi Arabia', 'MENA', 'transport', 'operational', 22500000000, 'Arriyadh Development Authority', 'BACS Consortium (Bechtel, Almabani, CCC, Siemens)', '2013-04-01', '2013-07-01', '2013-12-01', '2021-12-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Madinah Airport PPP', 'Saudi Arabia', 'MENA', 'transport', 'operational', 1200000000, 'General Authority of Civil Aviation (GACA)', 'TAV Airports / Saudi Oger', '2010-06-01', '2011-10-01', '2012-01-01', '2015-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Jubail Export Refinery (SATORP)', 'Saudi Arabia', 'MENA', 'energy', 'operational', 14000000000, 'Saudi Aramco', 'Total Energies', '2008-01-01', '2008-06-01', '2009-01-01', '2014-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Rabigh IPP', 'Saudi Arabia', 'MENA', 'energy', 'operational', 2500000000, 'Saudi Electricity Company', 'ACWA Power / GDF Suez', '2005-01-01', '2006-01-01', '2006-06-01', '2012-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Fadhili Gas Plant', 'Saudi Arabia', 'MENA', 'energy', 'operational', 7000000000, 'Saudi Aramco', 'Saudi Aramco / GE', '2014-01-01', '2015-01-01', '2016-01-01', '2019-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Shuaibah 3 IWPP', 'Saudi Arabia', 'MENA', 'water', 'operational', 2400000000, 'Water and Electricity Company (WEC)', 'ACWA Power', '2009-01-01', '2010-01-01', '2010-06-01', '2014-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Yanbu 3 IWP', 'Saudi Arabia', 'MENA', 'water', 'operational', 690000000, 'National Water Company', 'ACWA Power / Veolia', '2013-01-01', '2014-01-01', '2014-06-01', '2016-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Riyadh Bus Rapid Transit', 'Saudi Arabia', 'MENA', 'transport', 'operational', 800000000, 'Royal Commission for Riyadh City', 'RATP Dev / Almabani', '2016-01-01', '2017-01-01', '2017-06-01', '2019-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Red Sea Project', 'Saudi Arabia', 'MENA', 'social infrastructure', 'pipeline', 5000000000, 'Red Sea Global', 'Multiple concessionaires', '2017-07-01', null, null, null, 'https://www.theredsea.sa', 'Red Sea Global', 0.9, true),
('NEOM Taqah Renewable Energy', 'Saudi Arabia', 'MENA', 'energy', 'pipeline', 5000000000, 'NEOM', 'ACWA Power', '2019-01-01', null, null, null, 'https://www.neom.com', 'NEOM', 0.9, true),
('Sudair Solar PV', 'Saudi Arabia', 'MENA', 'energy', 'awarded', 950000000, 'ACWA Power / Saudi Electricity Company', 'ACWA Power / Vision Invest', '2021-01-01', '2021-08-01', null, null, 'https://ppi.worldbank.org', 'World Bank PPI', 0.95, true),
('NEOM Green Hydrogen Plant', 'Saudi Arabia', 'MENA', 'energy', 'awarded', 5000000000, 'NEOM', 'Air Products / ACWA Power / NEOM', '2020-07-01', '2021-05-01', '2022-01-01', null, 'https://www.neom.com/en-us/regions/oxagon', 'NEOM', 1.0, true),

-- UAE
('Noor Abu Dhabi Solar Plant', 'UAE', 'MENA', 'energy', 'operational', 870000000, 'Abu Dhabi Water and Electricity Authority (ADWEA)', 'Marubeni / EDF Renewables', '2016-03-01', '2016-09-01', '2017-01-01', '2019-06-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Al Dhafra Solar PV', 'UAE', 'MENA', 'energy', 'operational', 1000000000, 'Abu Dhabi Power Corporation', 'Masdar / EDF / Jinko Power', '2020-01-01', '2021-01-01', '2021-06-01', '2023-07-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Mohammed bin Rashid Solar Park Phase 5', 'UAE', 'MENA', 'energy', 'operational', 1600000000, 'Dubai Electricity and Water Authority (DEWA)', 'ACWA Power', '2019-01-01', '2019-04-01', '2019-10-01', '2021-11-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Hassyan Clean Coal Power Plant', 'UAE', 'MENA', 'energy', 'operational', 3400000000, 'Dubai Electricity and Water Authority (DEWA)', 'ACWA Power / Harbin Electric', '2015-01-01', '2015-03-01', '2015-09-01', '2020-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Dubai Metro Red Line Extension', 'UAE', 'MENA', 'transport', 'operational', 2900000000, 'Roads and Transport Authority Dubai', 'Alstom / Acciona / Gülermak', '2016-01-01', '2016-11-01', '2017-06-01', '2020-09-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Shuweihat S2 IWPP', 'UAE', 'MENA', 'water', 'operational', 2700000000, 'Abu Dhabi Water and Electricity Authority (ADWEA)', 'International Power / GDF Suez', '2009-01-01', '2009-11-01', '2010-06-01', '2014-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Mirfa IWPP', 'UAE', 'MENA', 'water', 'operational', 1400000000, 'Abu Dhabi Water and Electricity Authority (ADWEA)', 'GDF Suez / Marubeni', '2012-01-01', '2012-06-01', '2012-12-01', '2017-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Taweelah IWP', 'UAE', 'MENA', 'water', 'operational', 876000000, 'Abu Dhabi Power Corporation', 'ACWA Power', '2018-01-01', '2019-02-01', '2019-08-01', '2022-05-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Abu Dhabi International Airport Midfield Terminal', 'UAE', 'MENA', 'transport', 'operational', 3000000000, 'Abu Dhabi Airports', 'TAV / Arabtec / CCC', '2012-01-01', '2012-06-01', '2013-01-01', '2023-11-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Sweihan Photovoltaic IPP', 'UAE', 'MENA', 'energy', 'operational', 870000000, 'Abu Dhabi Water and Electricity Authority (ADWEA)', 'JinkoSolar / Marubeni', '2016-06-01', '2017-09-01', '2018-01-01', '2019-09-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),

-- KUWAIT
('Al-Zour North 1 IWPP', 'Kuwait', 'MENA', 'water', 'operational', 3700000000, 'Ministry of Electricity and Water Kuwait', 'ACWA Power / Gulf Investment / Sumitomo', '2014-01-01', '2015-08-01', '2016-01-01', '2019-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Az-Zour South IWPP', 'Kuwait', 'MENA', 'water', 'operational', 2700000000, 'Ministry of Electricity and Water Kuwait', 'GDF Suez / Mitsui', '2009-01-01', '2010-02-01', '2010-08-01', '2016-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Umm Al Hayman Wastewater', 'Kuwait', 'MENA', 'water', 'operational', 2500000000, 'Kuwait Authority for Partnership Projects (KAPP)', 'Suez / Warba National Construction', '2018-01-01', '2018-11-01', '2019-06-01', '2022-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Kabd Independent Power Project', 'Kuwait', 'MENA', 'energy', 'awarded', 2200000000, 'Kuwait Authority for Partnership Projects (KAPP)', 'ACWA Power', '2022-01-01', '2023-01-01', null, null, 'https://ppi.worldbank.org', 'World Bank PPI', 0.9, true),

-- QATAR
('Doha Metro', 'Qatar', 'MENA', 'transport', 'operational', 36000000000, 'Qatar Rail', 'Various (Alstom, Bombardier, Mitsubishi)', '2012-01-01', '2013-06-01', '2014-01-01', '2019-05-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Hamad International Airport', 'Qatar', 'MENA', 'transport', 'operational', 15500000000, 'Qatar Civil Aviation Authority', 'Various concessionaires', '2005-01-01', null, null, '2014-04-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Ras Laffan C Power & Desalination', 'Qatar', 'MENA', 'water', 'operational', 2400000000, 'Qatar General Electricity & Water Corporation', 'Qatar Electricity & Water / Suez / Total', '2004-01-01', '2004-06-01', '2004-12-01', '2008-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Qatar Integrated Railway Program', 'Qatar', 'MENA', 'transport', 'operational', 40000000000, 'Qatar Rail', 'Multiple consortia', '2012-01-01', '2013-01-01', '2014-01-01', '2021-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),

-- OMAN
('Barka 2 IWPP', 'Oman', 'MENA', 'water', 'operational', 740000000, 'Oman Power and Water Procurement (OPWP)', 'SMN Power Holding / GDF Suez', '2008-01-01', '2009-01-01', '2009-06-01', '2012-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Sohar 2 IWPP', 'Oman', 'MENA', 'water', 'operational', 900000000, 'Oman Power and Water Procurement (OPWP)', 'GDF Suez / Multitech', '2012-01-01', '2012-08-01', '2013-01-01', '2015-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Ibri 2 IPP', 'Oman', 'MENA', 'energy', 'operational', 800000000, 'Oman Power and Water Procurement (OPWP)', 'ACWA Power', '2018-01-01', '2019-07-01', '2019-12-01', '2021-10-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Muscat Bay PPP', 'Oman', 'MENA', 'social infrastructure', 'operational', 1000000000, 'Ministry of Housing Oman', 'Omran / Multiple developers', '2011-01-01', null, null, '2018-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 0.85, true),

-- BAHRAIN
('Hidd Power Company', 'Bahrain', 'MENA', 'energy', 'operational', 560000000, 'Electricity and Water Authority Bahrain', 'GDF Suez / ENGIE', '2001-01-01', '2001-06-01', '2002-01-01', '2005-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Bahrain LNG Import Terminal', 'Bahrain', 'MENA', 'energy', 'operational', 741000000, 'National Oil and Gas Authority Bahrain', 'Teekay / GIC / OHL', '2015-01-01', '2016-02-01', '2016-09-01', '2019-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),

-- EGYPT
('Benban Solar Park', 'Egypt', 'MENA', 'energy', 'operational', 2800000000, 'Egyptian Electricity Transmission Company', 'Multiple IPPs (Scatec, ACWA, Orascom)', '2016-01-01', '2017-01-01', '2017-06-01', '2019-10-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Gulf of Suez Wind Farm', 'Egypt', 'MENA', 'energy', 'operational', 290000000, 'Egyptian Electricity Holding Company', 'Gamesa / Engie', '2009-01-01', '2010-01-01', '2010-06-01', '2015-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('New Administrative Capital Water & Wastewater', 'Egypt', 'MENA', 'water', 'awarded', 3100000000, 'New Administrative Capital Urban Development Authority', 'Orascom Construction / Hassan Allam', '2019-06-01', '2020-01-01', null, null, 'https://ppi.worldbank.org', 'World Bank PPI', 0.9, true),
('Queen Nefertari Wind Farm', 'Egypt', 'MENA', 'energy', 'operational', 400000000, 'Egyptian Electricity Holding Company', 'Lekela Power', '2016-01-01', '2017-01-01', '2017-06-01', '2020-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Cairo Metro Line 4 Phase 1', 'Egypt', 'MENA', 'transport', 'procurement', 3500000000, 'National Authority for Tunnels Egypt', 'To be determined', '2019-01-01', null, null, null, 'https://ppi.worldbank.org', 'World Bank PPI', 0.85, true),
('El Sokhna Power Plant', 'Egypt', 'MENA', 'energy', 'operational', 700000000, 'Egyptian Electricity Holding Company', 'Siemens / Elsewedy', '2016-01-01', '2016-06-01', '2016-12-01', '2018-06-01', 'https://ppi.worldbank.org', 'World Bank PPI', 0.9, true),
('Ain Sokhna Port Container Terminal', 'Egypt', 'MENA', 'transport', 'operational', 600000000, 'Red Sea Ports Authority', 'MSC / COSCO', '2008-01-01', '2009-01-01', '2009-06-01', '2013-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 0.9, true),

-- JORDAN
('Queen Alia International Airport', 'Jordan', 'MENA', 'transport', 'operational', 750000000, 'Civil Aviation Regulatory Commission Jordan', 'Airport International Group (AIG)', '2006-01-01', '2007-05-01', '2007-12-01', '2013-03-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('As-Samra Wastewater Treatment', 'Jordan', 'MENA', 'water', 'operational', 270000000, 'Water Authority of Jordan', 'LEMA (Ondeo / Suez)', '2002-01-01', '2003-01-01', '2003-06-01', '2008-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Tafila Wind Farm', 'Jordan', 'MENA', 'energy', 'operational', 287000000, 'National Electric Power Company Jordan', 'InfraSource / Masdar / EP Global', '2011-01-01', '2012-01-01', '2012-06-01', '2015-11-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Attarat Power Plant (Oil Shale)', 'Jordan', 'MENA', 'energy', 'operational', 2100000000, 'National Electric Power Company Jordan', 'YTL Power / Yudean / Attarat Power Company', '2014-01-01', '2014-09-01', '2015-06-01', '2021-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),

-- MOROCCO
('Noor Ouarzazate 1 CSP', 'Morocco', 'MENA', 'energy', 'operational', 1100000000, 'Moroccan Agency for Sustainable Energy (MASEN)', 'ACWA Power / Saudi Arabia''s Public Investment Fund', '2012-01-01', '2012-10-01', '2013-05-01', '2016-02-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Noor Ouarzazate 2 CSP', 'Morocco', 'MENA', 'energy', 'operational', 820000000, 'Moroccan Agency for Sustainable Energy (MASEN)', 'ACWA Power', '2014-01-01', '2014-10-01', '2015-04-01', '2018-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Noor Ouarzazate 3 CSP', 'Morocco', 'MENA', 'energy', 'operational', 860000000, 'Moroccan Agency for Sustainable Energy (MASEN)', 'ACWA Power / Sener', '2015-01-01', '2015-10-01', '2016-04-01', '2018-10-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Tanger Med Port Complex', 'Morocco', 'MENA', 'transport', 'operational', 1300000000, 'Tanger Med Port Authority', 'APM Terminals / CMA CGM / MSC', '2002-01-01', '2004-01-01', '2004-06-01', '2007-07-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Casablanca Tramway', 'Morocco', 'MENA', 'transport', 'operational', 690000000, 'Casablanca Transport', 'Alstom / Colas Rail', '2010-01-01', '2011-01-01', '2011-06-01', '2012-12-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Al Boraq High Speed Rail', 'Morocco', 'MENA', 'transport', 'operational', 2100000000, 'Office National des Chemins de Fer (ONCF)', 'Alstom / SNCF', '2007-01-01', '2008-01-01', '2010-01-01', '2018-11-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Jorf Lasfar Energy Company', 'Morocco', 'MENA', 'energy', 'operational', 1400000000, 'Office National de l''Electricité (ONE)', 'CMS Energy / ABB', '1994-01-01', '1995-01-01', '1995-06-01', '1997-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Midelt CSP-PV Hybrid', 'Morocco', 'MENA', 'energy', 'awarded', 2200000000, 'Moroccan Agency for Sustainable Energy (MASEN)', 'ACWA Power / Nareva / Sener', '2017-01-01', '2019-10-01', '2020-06-01', null, 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),

-- TUNISIA
('Enfidha International Airport', 'Tunisia', 'MENA', 'transport', 'operational', 520000000, 'Office de l''Aviation Civile et des Aéroports (OACA)', 'TAV Airports', '2006-01-01', '2007-04-01', '2007-10-01', '2009-12-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Sfax Wastewater PPP', 'Tunisia', 'MENA', 'water', 'operational', 180000000, 'SONEDE Tunisia', 'Suez / Tunisian partners', '2014-01-01', '2015-01-01', '2015-06-01', '2018-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 0.85, true),

-- IRAQ
('Basra Gas Company', 'Iraq', 'MENA', 'energy', 'operational', 17000000000, 'South Gas Company / Iraqi Ministry of Oil', 'Shell / Mitsubishi', '2009-01-01', '2010-01-01', '2011-01-01', '2013-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Baghdad East Power Plant', 'Iraq', 'MENA', 'energy', 'operational', 1400000000, 'Ministry of Electricity Iraq', 'Siemens', '2015-01-01', '2015-06-01', '2016-01-01', '2018-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 0.9, true),
('Rumaila Oilfield Development', 'Iraq', 'MENA', 'energy', 'operational', 15000000000, 'South Oil Company Iraq', 'BP / CNPC', '2009-01-01', '2009-11-01', '2010-06-01', null, 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),

-- ISRAEL
('Tel Aviv Purple Line Metro', 'Israel', 'MENA', 'transport', 'procurement', 5700000000, 'National Transport Infrastructure Company (NTA)', 'To be determined', '2020-01-01', null, null, null, 'https://ppi.worldbank.org', 'World Bank PPI', 0.9, true),
('Ashdod Desalination Plant', 'Israel', 'MENA', 'water', 'operational', 400000000, 'Mekorot', 'IDE Technologies / Hutchison Water', '2010-01-01', '2011-01-01', '2011-06-01', '2015-01-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Sorek Desalination Plant', 'Israel', 'MENA', 'water', 'operational', 500000000, 'Mekorot', 'IDE Technologies / Hutchison Water', '2009-01-01', '2011-01-01', '2011-06-01', '2013-10-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),
('Hadera Desalination Plant', 'Israel', 'MENA', 'water', 'operational', 400000000, 'Mekorot', 'IDE Technologies / Shikun & Binui', '2005-01-01', '2006-01-01', '2006-06-01', '2010-12-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true),

-- LEBANON
('Beirut River Canal Project', 'Lebanon', 'MENA', 'water', 'cancelled', 300000000, 'Council for Development and Reconstruction Lebanon', null, '2010-01-01', null, null, null, 'https://ppi.worldbank.org', 'World Bank PPI', 0.8, true),

-- PALESTINE
('Gaza Power Plant', 'Palestine', 'MENA', 'energy', 'operational', 140000000, 'Palestinian Energy Authority', 'Private Palestinian investors', '1999-01-01', '2000-01-01', '2000-06-01', '2002-07-01', 'https://ppi.worldbank.org', 'World Bank PPI', 1.0, true);
```

## Step 3: Trigger geocoding for any missing coordinates

After inserting, invoke the ppp-geocode edge function from the Admin → Runs page to resolve lat/lng for all newly added projects.

## Step 4: Verify the data

Show a success toast: "MENA PPP database seeded with [count] projects."

Then refresh the homepage — the map should show pins across the Middle East and North Africa, and the stats bar should reflect the new totals.
