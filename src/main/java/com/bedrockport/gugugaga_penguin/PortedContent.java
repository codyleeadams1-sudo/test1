package com.bedrockport.gugugaga_penguin;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;

/** Main entrypoint: registers the penguin, its sounds and its spawn egg. */
public class PortedContent implements ModInitializer {
    public static final String MOD_ID = "gugugaga_penguin";

    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MOD_ID, path);
    }

    private static SoundEvent registerSound(String name) {
        Identifier id = id(name);
        return Registry.register(BuiltInRegistries.SOUND_EVENT, id, SoundEvent.createVariableRangeEvent(id));
    }

    // names match sounds.json
    public static final SoundEvent SOUND_IDLE = registerSound("mob.gugugaga.idle");
    public static final SoundEvent SOUND_HURT = registerSound("mob.gugugaga.hurt");
    public static final SoundEvent SOUND_DEATH = registerSound("mob.gugugaga.death");
    public static final SoundEvent SOUND_CRY = registerSound("mob.gugugaga.cry");

    private static final ResourceKey<EntityType<?>> PENGUIN_KEY =
            ResourceKey.create(Registries.ENTITY_TYPE, id("gugugaga_penguin"));

    public static final EntityType<PenguinEntity> PENGUIN = Registry.register(
            BuiltInRegistries.ENTITY_TYPE, PENGUIN_KEY,
            EntityType.Builder.of(PenguinEntity::new, MobCategory.CREATURE)
                    .sized(0.5f, 1.0f)
                    .build(PENGUIN_KEY));

    private static final ResourceKey<Item> EGG_KEY =
            ResourceKey.create(Registries.ITEM, id("gugugaga_penguin_spawn_egg"));

    public static final Item PENGUIN_SPAWN_EGG = Registry.register(
            BuiltInRegistries.ITEM, EGG_KEY,
            new SpawnEggItem(new Item.Properties().setId(EGG_KEY).spawnEgg(PENGUIN)));

    @Override
    public void onInitialize() {
        FabricDefaultAttributeRegistry.register(PENGUIN, PenguinEntity.createAttributes());
        SpawnPlacements.register(PENGUIN, SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mob::checkMobSpawnRules);

        // Spawn rules from gugugaga_spawn.json (weights scaled down: Bedrock 200/10/2 -> 20/2/1)
        BiomeModifications.addSpawn(BiomeSelectors.includeByKey(Biomes.SNOWY_PLAINS, Biomes.ICE_SPIKES,
                Biomes.SNOWY_TAIGA, Biomes.SNOWY_SLOPES, Biomes.FROZEN_PEAKS, Biomes.JAGGED_PEAKS, Biomes.GROVE),
                MobCategory.CREATURE, PENGUIN, 20, 2, 5);
        BiomeModifications.addSpawn(BiomeSelectors.includeByKey(Biomes.PLAINS, Biomes.FOREST, Biomes.JUNGLE),
                MobCategory.CREATURE, PENGUIN, 2, 1, 1);
        BiomeModifications.addSpawn(BiomeSelectors.includeByKey(Biomes.DESERT),
                MobCategory.CREATURE, PENGUIN, 1, 1, 1);

        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.SPAWN_EGGS)
                .register(entries -> entries.accept(PENGUIN_SPAWN_EGG));
    }
}
