#!/bin/sh
# Regenerates PenguinModel.java + the repacked texture from the original Bedrock files.
python3 tools/bedrock_geo_to_java.py tools/bedrock_source/gugugaga.geo.json tools/bedrock_source/gugugaga_penguin.png \
  src/main/java/com/bedrockport/gugugaga_penguin/PenguinModel.java src/main/resources/assets/gugugaga_penguin/textures/entity/gugugaga_penguin.png com.bedrockport.gugugaga_penguin
