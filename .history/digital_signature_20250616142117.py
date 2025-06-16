import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont
import os
import math

class DigitalSignatureGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("전자서명 및 전자도장 생성기")
        self.root.geometry("800x600")
        
        # 기본 설정
        self.text = tk.StringVar(value="홍길동")
        self.signature_color = "#000080"  # 네이비 블루
        self.stamp_color = "#CC0000"      # 빨간색
        self.bg_color = "#FFFFFF"         # 흰색
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 텍스트 입력 섹션
        input_frame = ttk.LabelFrame(main_frame, text="입력 설정", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="이름/텍스트:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.text, width=30).grid(row=0, column=1, padx=5)
        
        # 전자서명 섹션
        signature_frame = ttk.LabelFrame(main_frame, text="전자서명 생성", padding="10")
        signature_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        ttk.Button(signature_frame, text="색상 선택", 
                  command=lambda: self.choose_color('signature')).grid(row=0, column=0, pady=5)
        
        ttk.Button(signature_frame, text="필기체 서명 생성", 
                  command=lambda: self.generate_signature('cursive')).grid(row=1, column=0, pady=2)
        ttk.Button(signature_frame, text="세련된 서명 생성", 
                  command=lambda: self.generate_signature('elegant')).grid(row=2, column=0, pady=2)
        ttk.Button(signature_frame, text="단순 서명 생성", 
                  command=lambda: self.generate_signature('simple')).grid(row=3, column=0, pady=2)
        
        # 전자도장 섹션
        stamp_frame = ttk.LabelFrame(main_frame, text="전자도장 생성", padding="10")
        stamp_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        ttk.Button(stamp_frame, text="색상 선택", 
                  command=lambda: self.choose_color('stamp')).grid(row=0, column=0, pady=5)
        
        ttk.Button(stamp_frame, text="원형 도장 생성", 
                  command=lambda: self.generate_stamp('circle')).grid(row=1, column=0, pady=2)
        ttk.Button(stamp_frame, text="사각 도장 생성", 
                  command=lambda: self.generate_stamp('square')).grid(row=2, column=0, pady=2)
        ttk.Button(stamp_frame, text="전통 도장 생성", 
                  command=lambda: self.generate_stamp('traditional')).grid(row=3, column=0, pady=2)
        
        # 미리보기 섹션
        preview_frame = ttk.LabelFrame(main_frame, text="미리보기", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.preview_label = ttk.Label(preview_frame, text="생성된 이미지가 여기에 표시됩니다.")
        self.preview_label.grid(row=0, column=0)
        
        # 저장 버튼
        ttk.Button(main_frame, text="이미지 저장", 
                  command=self.save_image).grid(row=3, column=0, columnspan=2, pady=10)
        
        # 현재 이미지 저장용
        self.current_image = None
        
    def choose_color(self, color_type):
        color = colorchooser.askcolor(title="색상 선택")[1]
        if color:
            if color_type == 'signature':
                self.signature_color = color
            else:
                self.stamp_color = color
    
    def get_font(self, style, size):
        """사용 가능한 폰트를 찾아서 반환합니다."""
        # 시스템별 폰트 경로
        font_paths = []
        
        # Windows
        if os.name == 'nt':
            font_paths.extend([
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/times.ttf',
                'C:/Windows/Fonts/malgun.ttf',  # 맑은 고딕
                'C:/Windows/Fonts/gulim.ttc',   # 굴림
            ])
        
        # macOS
        elif os.name == 'posix' and os.uname().sysname == 'Darwin':
            font_paths.extend([
                '/System/Library/Fonts/Arial.ttf',
                '/System/Library/Fonts/Times.ttc',
                '/System/Library/Fonts/AppleGothic.ttf',
            ])
        
        # Linux
        else:
            font_paths.extend([
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            ])
        
        # 폰트 파일 찾기
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        # 기본 폰트 사용 (크기 지정)
        try:
            return ImageFont.load_default()
        except:
            # 최후의 수단으로 기본 폰트 사용
            return ImageFont.load_default()
    
    def generate_signature(self, style):
        if not self.text.get().strip():
            messagebox.showwarning("경고", "텍스트를 입력해주세요.")
            return
        
        # 이미지 크기 설정
        width, height = 400, 150
        
        # 이미지 생성
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 폰트 설정
        font_sizes = {'cursive': 40, 'elegant': 45, 'simple': 35}
        font_size = font_sizes.get(style, 40)
        font = self.get_font(style, font_size)
        
        # 텍스트 크기 계산
        text = self.text.get()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 텍스트 위치 계산
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # 스타일별 효과 적용
        if style == 'cursive':
            # 기울어진 효과
            draw.text((x, y), text, font=font, fill=self.signature_color)
            # 밑줄 추가
            draw.line([(x, y + text_height + 5), (x + text_width, y + text_height + 5)], 
                     fill=self.signature_color, width=2)
        
        elif style == 'elegant':
            # 그림자 효과
            draw.text((x + 2, y + 2), text, font=font, fill='#CCCCCC')
            draw.text((x, y), text, font=font, fill=self.signature_color)
        
        else:  # simple
            draw.text((x, y), text, font=font, fill=self.signature_color)
        
        self.current_image = img
        self.show_preview(img)
    
    def generate_stamp(self, style):
        if not self.text.get().strip():
            messagebox.showwarning("경고", "텍스트를 입력해주세요.")
            return
        
        # 이미지 크기 설정
        size = 150
        
        # 이미지 생성
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        text = self.text.get()
        
        if style == 'circle':
            # 원형 테두리
            draw.ellipse([10, 10, size-10, size-10], outline=self.stamp_color, width=3)
            
            # 텍스트
            font = self.get_font('stamp', 30)
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, font=font, fill=self.stamp_color)
        
        elif style == 'square':
            # 사각형 테두리
            draw.rectangle([10, 10, size-10, size-10], outline=self.stamp_color, width=3)
            
            # 텍스트
            font = self.get_font('stamp', 28)
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, font=font, fill=self.stamp_color)
        
        else:  # traditional
            # 전통적인 원형 도장 스타일
            draw.ellipse([5, 5, size-5, size-5], outline=self.stamp_color, width=5)
            
            # 내부 원
            draw.ellipse([20, 20, size-20, size-20], outline=self.stamp_color, width=2)
            
            # 텍스트 (세로 배치)
            font = self.get_font('stamp', 24)
            
            # 텍스트를 세로로 배치
            if len(text) > 1:
                char_height = 25
                total_height = len(text) * char_height
                start_y = (size - total_height) // 2
                
                for i, char in enumerate(text):
                    bbox = draw.textbbox((0, 0), char, font=font)
                    char_width = bbox[2] - bbox[0]
                    x = (size - char_width) // 2
                    y = start_y + i * char_height
                    draw.text((x, y), char, font=font, fill=self.stamp_color)
            else:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (size - text_width) // 2
                y = (size - text_height) // 2
                draw.text((x, y), text, font=font, fill=self.stamp_color)
        
        self.current_image = img
        self.show_preview(img)
    
    def show_preview(self, img):
        # 미리보기용 이미지 크기 조정
        preview_img = img.copy()
        preview_img.thumbnail((300, 200), Image.Resampling.LANCZOS)
        
        # tkinter에서 표시할 수 있도록 변환
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(preview_img)
        
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo  # 참조 유지
    
    def save_image(self):
        if self.current_image is None:
            messagebox.showwarning("경고", "저장할 이미지가 없습니다.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if filename:
            # 투명 배경을 흰색으로 변경하여 저장
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                # JPG는 투명도를 지원하지 않으므로 흰색 배경 추가
                background = Image.new('RGB', self.current_image.size, (255, 255, 255))
                background.paste(self.current_image, mask=self.current_image.split()[-1])
                background.save(filename, quality=95)
            else:
                self.current_image.save(filename)
            
            messagebox.showinfo("완료", f"이미지가 저장되었습니다: {filename}")

def main():
    root = tk.Tk()
    app = DigitalSignatureGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()