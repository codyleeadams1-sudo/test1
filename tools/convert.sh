#!/bin/sh
# Regenerates PenguinModel.java + the repacked texture from the original Bedrock files.
python3 tools/bedrock_geo_to_java.py tools/bedrock_source/gugugaga.geo.json tools/bedrock_source/gugugaga_penguin.png \
  src/main/java/com/bedrockport/b_gugugaga_penguin_bp_a_full_version_english_version_e_by_dlt_craft/PenguinModel.java src/main/resources/assets/b_gugugaga_penguin_bp_a_full_version_english_version_e_by_dlt_craft/textures/entity/gugugaga_penguin.png com.bedrockport.b_gugugaga_penguin_bp_a_full_version_english_version_e_by_dlt_craft
