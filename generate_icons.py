import os
from PIL import Image, ImageDraw

def generate_tauri_icons():
    icon_dir = os.path.join('src-tauri', 'icons')
    os.makedirs(icon_dir, exist_ok=True)

    # 256x256 base image
    img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw orange cat circle background
    draw.ellipse((16, 16, 240, 240), fill=(255, 158, 62, 255))
    
    # Cat Ears
    draw.polygon([(40, 60), (80, 20), (100, 70)], fill=(235, 120, 40, 255))
    draw.polygon([(156, 70), (176, 20), (216, 60)], fill=(235, 120, 40, 255))
    
    # Eyes
    draw.ellipse((75, 100, 105, 130), fill=(255, 255, 255, 255))
    draw.ellipse((85, 110, 95, 120), fill=(30, 30, 30, 255))
    draw.ellipse((151, 100, 181, 130), fill=(255, 255, 255, 255))
    draw.ellipse((161, 110, 171, 120), fill=(30, 30, 30, 255))
    
    # Nose
    draw.polygon([(120, 140), (136, 140), (128, 150)], fill=(243, 139, 168, 255))

    # Save all required Tauri icon formats
    img.resize((32, 32)).save(os.path.join(icon_dir, '32x32.png'))
    img.resize((128, 128)).save(os.path.join(icon_dir, '128x128.png'))
    img.resize((256, 256)).save(os.path.join(icon_dir, '128x128@2x.png'))
    img.save(os.path.join(icon_dir, 'icon.ico'), format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    img.save(os.path.join(icon_dir, 'icon.icns'), format='PNG')
    
    print("[OK] Berhasil membuat ikon Tauri di folder src-tauri/icons/:")
    print("  - src-tauri/icons/32x32.png")
    print("  - src-tauri/icons/128x128.png")
    print("  - src-tauri/icons/128x128@2x.png")
    print("  - src-tauri/icons/icon.ico")
    print("  - src-tauri/icons/icon.icns")

if __name__ == "__main__":
    generate_tauri_icons()
