
# EXEMPLO DE INTEGRAÇÃO DE COMANDOS DE VISUALIZAÇÃO
# Adicionar ao método processar_comando_backend() do assistente

# Comandos de visualização
if any(phrase in comando_lower for phrase in ["modo visual", "visualização", "preset visual"]):
    if "alterar" in comando_lower or "mudar" in comando_lower:
        if hasattr(self, 'hotword_detector') and self.hotword_detector:
            if hasattr(self.hotword_detector, 'toggle_visual_mode'):
                self.hotword_detector.toggle_visual_mode()
                resposta = "✨ Modo visual alterado!"
            else:
                resposta = "⚠️ Sistema visual não disponível"
        else:
            resposta = "❌ Detector de hotword não ativo"
    
    elif any(preset in comando_lower for preset in ["festa", "completo", "minimalista", "discreto"]):
        # Extrair nome do preset
        for preset_name in ["festa", "completo", "minimalista", "discreto"]:
            if preset_name in comando_lower:
                if hasattr(self, 'hotword_detector') and self.hotword_detector:
                    if hasattr(self.hotword_detector, 'set_visualization_preset'):
                        success = self.hotword_detector.set_visualization_preset(preset_name)
                        if success:
                            resposta = f"🎨 Preset '{preset_name}' aplicado com sucesso!"
                        else:
                            resposta = f"❌ Falha ao aplicar preset '{preset_name}'"
                    else:
                        resposta = "⚠️ Sistema visual não suporta presets"
                else:
                    resposta = "❌ Detector de hotword não ativo"
                break
    
    elif "desativar" in comando_lower:
        resposta = "🔇 Visualização será desativada na próxima sessão"
    elif "ativar" in comando_lower:
        resposta = "🎨 Visualização será ativada na próxima sessão"
