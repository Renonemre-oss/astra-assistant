#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Processador do Logo Original
Script para processar o logo original do ALEX e gerar todas as variantes necessárias
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.asset_manager import get_asset_manager
from PIL import Image, ImageEnhance, ImageFilter
import shutil

def process_original_logo():
    """Processa o logo original e gera todas as variantes."""
    print("🎨 Processando logo original do ALEX...")
    
    # Caminhos
    project_root = Path(__file__).parent.parent
    original_logo_path = project_root / "logo_ALEX.png"
    
    if not original_logo_path.exists():
        print(f"❌ Logo original não encontrado: {original_logo_path}")
        return False
    
    am = get_asset_manager()
    
    try:
        # Carregar logo original
        print(f"📂 Carregando logo original: {original_logo_path}")
        original_img = Image.open(original_logo_path)
        
        # Converter para RGBA se necessário
        if original_img.mode != 'RGBA':
            original_img = original_img.convert('RGBA')
        
        print(f"📐 Tamanho original: {original_img.size}")
        
        # Primeiro, copiar o original para a pasta de assets
        original_dest = am.assets_dir / "logos" / "alex_logo_original.png"
        os.makedirs(os.path.dirname(original_dest), exist_ok=True)
        shutil.copy2(original_logo_path, original_dest)
        print(f"✅ Logo original copiado para: {original_dest}")
        
        # Configurações das versões a gerar
        logo_variants = [
            {
                'name': 'alex_logo_main',
                'size': (512, 512),
                'path': 'logos/alex_logo_main.png',
                'description': 'Logo principal do ALEX - versão quadrada alta resolução',
                'enhance': True
            },
            {
                'name': 'alex_logo_horizontal',
                'size': (800, 300), 
                'path': 'logos/alex_logo_horizontal.png',
                'description': 'Logo horizontal do ALEX para interfaces largas',
                'enhance': True,
                'crop_to_fit': True
            },
            {
                'name': 'alex_favicon',
                'size': (64, 64),
                'path': 'favicons/alex_favicon.png',
                'description': 'Favicon do ALEX para navegadores e aplicações',
                'enhance': True
            },
            {
                'name': 'alex_app_icon',
                'size': (256, 256),
                'path': 'icons/alex_app_icon.png', 
                'description': 'Ícone da aplicação ALEX para Windows',
                'enhance': True
            }
        ]
        
        generated_count = 0
        
        for variant in logo_variants:
            print(f"\n📸 Gerando {variant['name']} ({variant['size'][0]}x{variant['size'][1]})...")
            
            # Redimensionar imagem
            if variant.get('crop_to_fit') and variant['size'][0] > variant['size'][1]:
                # Para logos horizontais, fazer crop inteligente
                processed_img = create_horizontal_version(original_img, variant['size'])
            else:
                # Redimensionamento normal mantendo proporção
                processed_img = original_img.copy()
                processed_img = processed_img.resize(variant['size'], Image.Resampling.LANCZOS)
            
            # Aplicar melhorias se especificado
            if variant.get('enhance'):
                processed_img = enhance_image(processed_img, variant['size'])
            
            # Salvar PNG
            png_path = am.assets_dir / variant['path']
            os.makedirs(os.path.dirname(png_path), exist_ok=True)
            processed_img.save(png_path, format='PNG', optimize=True)
            print(f"  ✅ {variant['name']}.png salvo")
            generated_count += 1
            
            # Gerar ICO se apropriado
            if variant['name'] in ['alex_logo_main', 'alex_favicon', 'alex_app_icon']:
                ico_path = png_path.with_suffix('.ico')
                create_ico_file(processed_img, ico_path, variant['size'])
                print(f"  ✅ {variant['name']}.ico salvo")
                generated_count += 1
        
        print(f"\n🎉 Processamento concluído! {generated_count} arquivos gerados.")
        
        # Atualizar registry do asset manager
        update_asset_registry(am)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_horizontal_version(img, target_size):
    """Cria versão horizontal do logo com layout apropriado."""
    target_width, target_height = target_size
    
    # Criar nova imagem com fundo transparente
    horizontal_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
    
    # Redimensionar logo original mantendo proporção
    img_copy = img.copy()
    
    # Calcular tamanho para caber na altura disponível
    aspect_ratio = img_copy.width / img_copy.height
    new_height = target_height - 40  # Margem
    new_width = int(new_height * aspect_ratio)
    
    # Se ficou muito largo, redimensionar pela largura
    if new_width > target_width * 0.4:  # Máximo 40% da largura
        new_width = int(target_width * 0.4)
        new_height = int(new_width / aspect_ratio)
    
    img_copy = img_copy.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Posicionar logo à esquerda
    x = 40  # Margem esquerda
    y = (target_height - new_height) // 2  # Centralizar verticalmente
    
    horizontal_img.paste(img_copy, (x, y), img_copy)
    
    # Adicionar texto "ALEX" à direita (simulado com fonte padrão)
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(horizontal_img)
        
        # Tentar usar uma fonte do sistema
        try:
            font_size = target_height // 4
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("calibri.ttf", target_height // 4)
            except:
                font = ImageFont.load_default()
        
        text = "ALEX"
        
        # Calcular posição do texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x + new_width + 40  # Após o logo com margem
        text_y = (target_height - text_height) // 2
        
        # Verificar se cabe
        if text_x + text_width < target_width - 20:
            # Sombra do texto
            draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 100), font=font)
            # Texto principal
            draw.text((text_x, text_y), text, fill=(245, 240, 230, 255), font=font)
    
    except Exception as e:
        print(f"  ⚠️ Aviso: Não foi possível adicionar texto: {e}")
    
    return horizontal_img

def enhance_image(img, target_size):
    """Aplica melhorias na imagem."""
    try:
        # Melhorar nitidez para tamanhos menores
        if max(target_size) <= 128:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
        
        # Melhorar contraste ligeiramente
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Para ícones muito pequenos, aplicar um filtro de suavização
        if max(target_size) <= 64:
            img = img.filter(ImageFilter.SMOOTH_MORE)
        
        return img
        
    except Exception as e:
        print(f"  ⚠️ Aviso: Não foi possível aplicar melhorias: {e}")
        return img

def create_ico_file(img, ico_path, base_size):
    """Cria arquivo ICO com múltiplos tamanhos."""
    try:
        # Definir tamanhos padrão para ICO
        if max(base_size) >= 256:
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        else:
            sizes = [(16, 16), (32, 32), (48, 48), base_size]
        
        # Criar imagens em diferentes tamanhos
        ico_images = []
        for size in sizes:
            if size == base_size:
                ico_img = img.copy()
            else:
                ico_img = img.resize(size, Image.Resampling.LANCZOS)
                # Aplicar melhorias para tamanhos pequenos
                if max(size) <= 48:
                    ico_img = enhance_image(ico_img, size)
            ico_images.append(ico_img)
        
        # Salvar ICO
        ico_images[0].save(
            ico_path, 
            format='ICO', 
            sizes=[(img.width, img.height) for img in ico_images]
        )
        
    except Exception as e:
        print(f"  ⚠️ Erro ao criar ICO: {e}")

def update_asset_registry(asset_manager):
    """Atualiza o registry de assets."""
    try:
        print("\n🔄 Atualizando registry de assets...")
        
        # Forçar recriação do registry
        asset_manager._create_initial_registry()
        
        print("✅ Registry atualizado!")
        
        # Mostrar estatísticas
        assets = asset_manager.list_all_assets()
        print(f"\n📊 Assets registrados: {len(assets)}")
        for name, asset in assets.items():
            formats = []
            for fmt in ['png', 'ico']:
                test_path = asset_manager.assets_dir / asset.path.name.replace('.png', f'.{fmt}')
                if test_path.exists():
                    formats.append(fmt.upper())
            
            print(f"  🎨 {name}: {', '.join(formats) if formats else 'PNG'}")
    
    except Exception as e:
        print(f"⚠️ Erro ao atualizar registry: {e}")

def main():
    """Função principal."""
    try:
        # Verificar se PIL está disponível
        import PIL
        success = process_original_logo()
        return 0 if success else 1
        
    except ImportError:
        print("❌ Pillow (PIL) não está instalado.")
        print("💡 Execute: pip install Pillow")
        return 1
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())