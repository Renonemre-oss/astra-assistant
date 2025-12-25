#!/usr/bin/env python3
"""
Script para gerar múltiplas versões do logo ALEX
Gera logos em diferentes formatos e tamanhos
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.asset_manager import get_asset_manager
from PIL import Image, ImageDraw, ImageFont
import io

def create_alex_logo(size=(512, 512), text_size=None):
    """
    Cria o logo do ALEX com design moderno
    
    Args:
        size: Tupla (width, height) para o tamanho da imagem
        text_size: Tamanho da fonte (None = automático baseado no tamanho)
    
    Returns:
        PIL.Image: Imagem do logo
    """
    width, height = size
    
    # Criar imagem com fundo transparente
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cores do design
    primary_color = (0, 123, 255)      # Azul moderno
    accent_color = (108, 117, 125)     # Cinza elegante
    highlight_color = (255, 193, 7)    # Amarelo/dourado para destaque
    
    # Calcular tamanho da fonte baseado no tamanho da imagem
    if text_size is None:
        text_size = max(width // 8, 32)
    
    # Desenhar círculo de fundo
    circle_size = min(width, height) * 0.8
    circle_x = (width - circle_size) // 2
    circle_y = (height - circle_size) // 2
    
    # Gradiente circular (simulado com múltiplos círculos)
    for i in range(int(circle_size // 2), 0, -2):
        alpha = int(200 * (i / (circle_size // 2)))
        color = (*primary_color, alpha)
        draw.ellipse([
            circle_x + (circle_size // 2) - i,
            circle_y + (circle_size // 2) - i,
            circle_x + (circle_size // 2) + i,
            circle_y + (circle_size // 2) + i
        ], fill=color)
    
    # Tentar carregar fonte personalizada, usar padrão se não encontrar
    try:
        font = ImageFont.truetype("arial.ttf", text_size)
    except:
        try:
            font = ImageFont.truetype("calibri.ttf", text_size)
        except:
            font = ImageFont.load_default()
    
    # Texto "ALEX"
    text = "ALEX"
    
    # Calcular posição centralizada do texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Sombra do texto
    shadow_offset = max(2, width // 200)
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
              fill=(0, 0, 0, 100), font=font)
    
    # Texto principal
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Adicionar elemento decorativo (linha de destaque)
    line_y = text_y + text_height + (height // 20)
    line_width = text_width * 0.8
    line_x = (width - line_width) // 2
    line_thickness = max(2, height // 100)
    
    draw.rectangle([
        line_x, line_y,
        line_x + line_width, line_y + line_thickness
    ], fill=highlight_color)
    
    return img

def generate_all_logos():
    """Gera todas as versões do logo"""
    print("🎨 Gerando logos do ALEX...")
    
    am = get_asset_manager()
    
    # Configurações dos logos
    logo_configs = [
        # Logo principal (quadrado)
        {
            'name': 'alex_logo_main',
            'size': (512, 512),
            'formats': ['png', 'ico'],
            'description': 'Logo principal do ALEX - versão quadrada alta resolução'
        },
        # Logo horizontal
        {
            'name': 'alex_logo_horizontal', 
            'size': (800, 300),
            'formats': ['png'],
            'description': 'Logo horizontal do ALEX para interfaces largas'
        },
        # Favicon
        {
            'name': 'alex_favicon',
            'size': (64, 64),
            'formats': ['png', 'ico'],
            'description': 'Favicon do ALEX para navegadores e aplicações'
        },
        # Ícone da aplicação
        {
            'name': 'alex_app_icon',
            'size': (256, 256),
            'formats': ['png', 'ico'],
            'description': 'Ícone da aplicação ALEX para Windows'
        }
    ]
    
    generated_count = 0
    
    for config in logo_configs:
        name = config['name']
        size = config['size']
        formats = config['formats']
        description = config['description']
        
        print(f"\n📸 Gerando {name} ({size[0]}x{size[1]})...")
        
        # Gerar a imagem
        logo_img = create_alex_logo(size)
        
        # Salvar em cada formato
        for fmt in formats:
            filename = f"{name}.{fmt}"
            # Construir caminho baseado no tipo de asset
            if 'favicon' in name:
                file_path = am.assets_dir / "favicons" / filename
            elif 'app_icon' in name or 'icon' in name:
                file_path = am.assets_dir / "icons" / filename
            else:
                file_path = am.assets_dir / "logos" / filename
            
            try:
                # Criar diretório se não existir
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                if fmt == 'ico':
                    # Para ICO, criar múltiplos tamanhos
                    sizes = []
                    if size[0] >= 256:
                        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                    else:
                        sizes = [(16, 16), (32, 32), (48, 48), size]
                    
                    ico_images = []
                    for ico_size in sizes:
                        if ico_size != size:
                            ico_img = logo_img.resize(ico_size, Image.Resampling.LANCZOS)
                        else:
                            ico_img = logo_img
                        ico_images.append(ico_img)
                    
                    ico_images[0].save(file_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
                else:
                    logo_img.save(file_path, format=fmt.upper())
                
                print(f"  ✅ {filename} salvo")
                generated_count += 1
                
            except Exception as e:
                print(f"  ❌ Erro ao salvar {filename}: {e}")
    
    print(f"\n🎉 Processo concluído! {generated_count} arquivos gerados.")
    
    # Listar assets registrados
    print(f"\n📋 Assets disponíveis:")
    for name, asset in am.list_all_assets().items():
        available_formats = []
        for fmt in ['png', 'ico', 'svg']:
            # Construir caminho baseado no tipo de asset
            if 'favicon' in name:
                file_path = am.assets_dir / f"favicons/{name}.{fmt}"
            elif 'app_icon' in name or 'icon' in name:
                file_path = am.assets_dir / f"icons/{name}.{fmt}"
            else:
                file_path = am.assets_dir / f"logos/{name}.{fmt}"
                
            if os.path.exists(file_path):
                available_formats.append(fmt.upper())
        
        print(f"  🎨 {name}")
        print(f"     📝 {asset.description}")
        if available_formats:
            print(f"     📁 Formatos: {', '.join(available_formats)}")
        else:
            print(f"     ⚠️  Nenhum arquivo encontrado")

if __name__ == "__main__":
    try:
        # Verificar se PIL está disponível
        import PIL
        generate_all_logos()
    except ImportError:
        print("❌ Pillow (PIL) não está instalado.")
        print("💡 Execute: pip install Pillow")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)