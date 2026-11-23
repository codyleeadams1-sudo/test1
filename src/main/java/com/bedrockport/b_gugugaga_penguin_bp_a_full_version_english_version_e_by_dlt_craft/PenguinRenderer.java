package com.bedrockport.b_gugugaga_penguin_bp_a_full_version_english_version_e_by_dlt_craft;

import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.resources.Identifier;

public class PenguinRenderer extends MobRenderer<PenguinEntity, LivingEntityRenderState, PenguinModel> {
    private static final Identifier TEXTURE = PortedContent.id("textures/entity/gugugaga_penguin.png");

    public PenguinRenderer(EntityRendererProvider.Context context) {
        super(context, new PenguinModel(context.bakeLayer(PortedContentClient.PENGUIN_LAYER)), 0.4F);
    }

    @Override
    public LivingEntityRenderState createRenderState() {
        return new LivingEntityRenderState();
    }

    @Override
    public Identifier getTextureLocation(LivingEntityRenderState state) {
        return TEXTURE;
    }
}
