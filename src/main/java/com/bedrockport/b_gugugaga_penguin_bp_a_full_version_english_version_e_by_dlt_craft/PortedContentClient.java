package com.bedrockport.b_gugugaga_penguin_bp_a_full_version_english_version_e_by_dlt_craft;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityModelLayerRegistry;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRenderers;

public class PortedContentClient implements ClientModInitializer {
    public static final ModelLayerLocation PENGUIN_LAYER =
            new ModelLayerLocation(PortedContent.id("gugugaga_penguin"), "main");

    @Override
    public void onInitializeClient() {
        EntityModelLayerRegistry.registerModelLayer(PENGUIN_LAYER, PenguinModel::createLayer);
        EntityRenderers.register(PortedContent.PENGUIN, PenguinRenderer::new);
    }
}
