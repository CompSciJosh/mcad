-- Joshua Jackson
-- Feb 5, 2025
-- MCAD: Lunar Navigation System

-- ###################################################
-- ######### Main SQL Statement For Database #########
-- ###################################################
/*
create or replace TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA (
	"Time (s)" VARCHAR(50) COMMENT 'This represents the timestamp of the data.',
	"SUN LoS" VARCHAR(80) COMMENT 'This array x,y,z represents the vector coordinates of the position of the Sun relative to the camera or spacecraft.',
	"Cam Pos (m)" VARCHAR(80) COMMENT 'This represents a spacecrafts position near the Moon or in space. The values are likely the camera’s position in space relative to a reference point (possibly the center of the Moon or Earth).',
	"Cam Quat (s)" FLOAT COMMENT 'This is the scalar part of the camera’s quaternion orientation. Quaternions are used to represent rotations in 3D space.',
	"Cam Quat (v)" VARCHAR(80) COMMENT 'This array represents the vector part of the camera’s quaternion. Along with the scalar part, it describes the camera’s orientation in 3D space.',
	"Cam LoS" VARCHAR(80) COMMENT 'This Line of Sight (LoS) describes the direction in which the camera is pointing in 3D space, given as a vector.',
	"FOV X (rad)" NUMBER(17,16) COMMENT 'This value indicates the angular width of the camera’s field of view along the horizontal axis.',
	"FOV Y (rad)" NUMBER(18,17) COMMENT 'This represents the vertical field of view, the height of the camera view.',
	"Nrows" NUMBER(38,0) COMMENT 'This is the number of rows in the camera’s image sensor, or the vertical resolution of the captured images. Vertical resolution of ____ pixels.',
	"Ncols" NUMBER(38,0) COMMENT 'This is the number of columns in the camera’s image sensor, or the horizontal resolution of the captured images. Horizontal resolution of ____ pixels.',
	"PNG File" VARCHAR(30) COMMENT 'Location of the PNG File',
	constraint UNIQUE_PNG_FILE unique ("PNG File")
);
*/

-- ###################################################
-- ###################################################

-- ###################################################################
-- #### Output Everything From a Specific Subfolder i.e. '001/%' #####
-- ###################################################################
-- SELECT * FROM mcad.mcad_data.moon_crater_data
-- WHERE "PNG File" LIKE '228/%';

-- ###################################################
-- ###################################################

-- #########################
-- #### Create Database ####
-- #########################
-- create database mcad;

-- ###################################################
-- ###################################################

-- #######################
-- #### Create Schema ####
-- #######################
-- create schema mcad_data;

-- ###################################################
-- ###################################################

-- ######################################
-- #### Create Table and its Columns ####
-- ######################################
-- create or replace table mcad.mcad_data.moon_crater_data (
-- 	Time_in_seconds VARCHAR (16777216),
-- 	SUN_LOS ARRAY,
-- 	Cam_Pos_in_meters ARRAY,
-- 	Cam_Quat_scalar NUMBER(18,16),
-- 	Cam_Quat_vector ARRAY,
-- 	Cam_LoS ARRAY,
-- 	FoV_X_rads NUMBER (21,20),
-- 	FoV_Y_rads NUMBER (18,16),
-- 	Nrows_Cam_Snsr NUMBER (38,0),
-- 	Ncols_Cam_Snsr NUMBER(38,0)
-- );
-- xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
-- xxxxx 👇🏾 Statement v.2 For JSON Data 👇🏾 xxxxx
-- xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
-- create or replace table mcad.mcad_data.moon_crater_data (
-- 	"Time (s)" VARCHAR(50) COMMENT 'This represents the timestamp of the data.',
-- 	"SUN LoS" VARCHAR(80) COMMENT 'This array x,y,z represents the vector coordinates of the position of the Sun relative to the camera or spacecraft.',
-- 	"Cam Pos (m)" VARCHAR(80) COMMENT 'This represents a spacecrafts position near the Moon or in space. The values are likely the camera’s position in space relative to a reference point (possibly the center of the Moon or Earth).',
-- 	"Cam Quat (s)" FLOAT COMMENT 'This is the scalar part of the camera’s quaternion orientation. Quaternions are used to represent rotations in 3D space.',
-- 	"Cam Quat (v)" VARCHAR(80) COMMENT 'This array represents the vector part of the camera’s quaternion. Along with the scalar part, it describes the camera’s orientation in 3D space.',
-- 	"Cam LoS" VARCHAR(80) COMMENT 'This Line of Sight (LoS) describes the direction in which the camera is pointing in 3D space, given as a vector.',
-- 	"FOV X (rad)" NUMBER (17,16) COMMENT 'This value indicates the angular width of the camera’s field of view along the horizontal axis.',
-- 	"FOV Y (rad)" NUMBER (18,17) COMMENT 'This represents the vertical field of view, the height of the camera view.',
-- 	"Nrows" INTEGER COMMENT 'This is the number of rows in the camera’s image sensor, or the vertical resolution of the captured images. Vertical resolution of ____ pixels.',
-- 	"Ncols" INTEGER COMMENT 'This is the number of columns in the camera’s image sensor, or the horizontal resolution of the captured images. Horizontal resolution of ____ pixels.',
-- "PNG File" VARCHAR(30) COMMENT 'Location of the PNG File',
-- CONSTRAINT unique_png_file UNIQUE ("PNG File")
-- ); -- Since Snowflaek does not enforce primary keys, I will use UNIQUE to prevent duplicate dta entries
-- ###################################################
-- ###################################################

-- ######################################################
-- ##### 🫵🏾 👍🏾 Create Database for BLOB Storage 🚀 ✅ ####
-- ######################################################
/*
If you want to store the actual PNG image data, you need to use
Snowflake's BLOB (binary large object) storage.
*/
-- CREATE OR REPLACE TABLE mcad.mcad_data.moon_crater_images (
--     "PNG File" VARCHAR(30) PRIMARY KEY COMMENT 'Location of the PNG file, in the format Folder {subfolder_name}/{file_name}',
--     "Image_Data" BINARY COMMENT 'Binary data of the PNG image'
-- );
-- ############################################################
-- ############################################################

-- #############################################################
-- #### 👍🏾 Load JSON Data From Internal Stage Into Table 👍🏾 #####
-- #############################################################
-- COPY INTO MCAD.MCAD_DATA.MOON_CRATER_DATA
-- FROM @internal_stage_for_original_data
-- FILE_FORMAT = (TYPE = 'JSON')
-- MATCH_BY_COLUMN_NAME = 'CASE_INSENSITIVE'
-- PATTERN = '.*\.json';  -- Load only JSON files

-- ###################################################
-- ###################################################

-- ##########################################
-- #### Search for Duplicate PNG Files  #####
-- ##########################################
-- SELECT "PNG File", COUNT(*)
-- FROM mcad.mcad_data.moon_crater_data
-- GROUP BY "PNG File"
-- HAVING COUNT(*) > 1;

-- ##########################################
-- #### Output Everything Table Columns #####
-- ##########################################
-- SELECT * FROM MCAD.MCAD_DATA.MOON_CRATER_DATA LIMIT 1000;

-- ###################################################
-- ###################################################

-- ###################################
-- #### Alter Table Column Names #####
-- ###################################
-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN TIME_IN_SECONDS TO "Time (s)";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN SUN_LOS TO "SUN LoS";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN CAM_POS_IN_METERS TO "Cam Pos (m)";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN CAM_QUAT_SCALAR TO "Cam Quat (s)";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN CAM_QUAT_VECTOR TO "Cam Quat (v)";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN CAM_LOS TO "Cam LoS";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN FOV_X_RADS TO "FOV X (rad)";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN FOV_Y_RADS TO "FOV Y (rad)";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN NROWS_CAM_SNSR TO "Nrows";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN NCOLS_CAM_SNSR TO "Ncols";

-- ###################################################
-- ###################################################

-- ################################################
-- #### Add a Column For the Path of the PNG  #####
-- ################################################
-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA ADD COLUMN "PNG FILE_PATH" STRING;

-- ###################################################
-- ###################################################

-- ################################################
-- #### Correct Typo of Column Name  #####
-- ################################################
-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- RENAME COLUMN "PNG File Path" TO "PNG File";

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- MODIFY COLUMN "Time (s)" VARCHAR(50);

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- MODIFY COLUMN "SUN LoS" VARCHAR(70);

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- MODIFY COLUMN "Cam Pos (m)" VARCHAR(70);

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- MODIFY COLUMN "Cam Quat (v)" VARCHAR(70);

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- MODIFY COLUMN "Cam LoS" VARCHAR(70);

-- ALTER TABLE MCAD.MCAD_DATA.MOON_CRATER_DATA
-- MODIFY COLUMN "PNG File" VARCHAR(25);

-- ###################################################
-- ###################################################

-- ######################################################################
-- #### Output Location of Data, Size in MB, md5, and Last Modified #####
-- ######################################################################
-- Ensures files are staged and correctly formatted
-- LIST @internal_stage_for_original_data;

-- ###################################################
-- ###################################################


-- COPY INTO MCAD.MCAD_DATA.MOON_CRATER_DATA
-- FROM (
--   SELECT
--     $1:"Time (s)"::STRING AS TIME_IN_SECONDS,
--     $1:"SUN LoS"::ARRAY AS SUN_LOS,
--     $1:"Cam Pos (m)"::ARRAY AS CAM_POS_IN_METERS,
--     $1:"Cam Quat (s)"::NUMBER AS CAM_QUAT_SCALAR,
--     $1:"Cam Quat (v)"::ARRAY AS CAM_QUAT_VECTOR,
--     $1:"Cam LoS"::ARRAY AS CAM_LOS,
--     $1:"FOV X (rad)"::NUMBER AS FOV_X_RADS,
--     $1:"FOV Y (rad)"::NUMBER AS FOV_Y_RADS,
--     $1:"Nrows"::NUMBER AS NROWS_CAM_SNSR,
--     $1:"Ncols"::NUMBER AS NCOLS_CAM_SNSR,
--     --NULL AS PNG_File_Path  -- Placeholder since JSON doesn't contain PNG paths
--   FROM @internal_stage_for_original_data
-- )
-- FILE_FORMAT = (TYPE = 'JSON')
-- PATTERN = '.*\.json';  -- Only load JSON files


-- LIST @internal_stage_for_original_data PATTERN = '.*\.json\.gz';


-- SELECT $1 FROM @internal_stage_for_original_data (FILE_FORMAT => (TYPE => 'JSON', COMPRESSION => 'AUTO')) LIMIT 5;


-- SELECT $1
-- FROM @internal_stage_for_original_data
-- (FILE_FORMAT => JSON);


-- SELECT COUNT(*) FROM MCAD.MCAD_DATA.MOON_CRATER_DATA;

-- SELECT
--     COUNT(*) AS total_rows,
--     COUNT(TIME_IN_SECONDS) AS time_non_null,
--     COUNT(SUN_LOS) AS sun_los_non_null,
--     COUNT(CAM_POS_IN_METERS) AS cam_pos_non_null
-- FROM MCAD.MCAD_DATA.MOON_CRATER_DATA;


-- SELECT $1 FROM @internal_stage_for_original_data LIMIT 5;


-- ##############################################
-- #### Table for Crater Detection results ######
-- # Maybe adjust this table to include a BLOB ##
-- ##### of the image with detected craters #####
-- ##############################################
CREATE TABLE crater_detection_results (
    image_id STRING,               -- Stores subfolder and filename (e.g., '001/image_0.png')
    detected_craters ARRAY,        -- Stores detected craters (list of dictionaries)
    crater_count INTEGER,          -- Number of craters detected
    processing_time FLOAT,         -- Time taken to process the image
    detection_timestamp TIMESTAMP  -- Timestamp when detection was performed
);

-- ################################################
-- ################################################













