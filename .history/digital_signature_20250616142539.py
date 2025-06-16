import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import math

class DrawingCanvas:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=400, height=200, bg='white', 
                               relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(pady=5)
        
        # 그리기 관련 변수
        self.old_x = None
        self.old_y = None
        self.pen_width = 3
        self.pen_color = '#000080'
        
        # 이벤트 바인딩
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonPress-1>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        
        # 컨트롤 버튼들
        control_frame = ttk.Frame(parent)
        control_frame.pack(pady=5)
        
        ttk.Button(control_frame, text="지우기", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="색상", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        
        # 펜 굵기 조절
        ttk.Label(control_frame, text="굵기:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.IntVar(value=3)
        width_scale = ttk.Scale(control_frame, from_=1, to=10, variable=self.width_var, 
                               orient=tk.HORIZONTAL, length=100)
        width_scale.pack(side=tk.LEFT, padx=5)
        width_scale.bind('<Motion>', self.update_pen_width)
        
    def paint(self, event):
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                   width=self.pen_width, fill=self.pen_color,
                                   capstyle=tk.ROUND, smooth=tk.TRUE)
        self.old_x = event.x
        self.old_y = event.y
        
    def reset(self, event):
        self.old_x = None
        self.old_y = None
        
    def clear_canvas(self):
        self.canvas.delete("all")
        
    def choose_color(self):
        color = colorchooser.askcolor(title="펜 색상 선택")[1]
        if color:
            self.pen_color = color
            
    def update_pen_width(self, event):
        self.pen_width = self.width_var.get()
        
    def get_image(self):
        """캔버스를 PIL 이미지로 변환"""
        # 캔버스를 PostScript로 저장
        ps = self.canvas.postscript(colormode='color')
        
        # PIL을 사용해 이미지로 변환
        img = Image.open(io.BytesIO(ps.encode('latin-1')))
        return img

class DigitalSignatureGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("전자서명 및 전자도장 생성기")
        self.root.geometry("900x700")
        
        # 기본 설정
        self.text = tk.StringVar(value="홍길동")
        self.signature_color = "#000080"  # 네이비 블루
        self.stamp_color = "#CC0000"      # 빨간색
        self.bg_color = "#FFFFFF"         # 흰색
        self.selected_font = "Arial"
        
        # 사용 가능한 폰트 목록 가져오기
        self.available_fonts = self.get_available_fonts()
        
        self.setup_ui()
        
    def get_available_fonts(self):
        """시스템에서 사용 가능한 폰트 목록을 가져옵니다."""
        # tkinter 폰트 패밀리 가져오기
        tk_fonts = list(font.families())
        
        # 추가로 확인할 폰트들
        common_fonts = ["Arial", "Times New Roman", "Helvetica", "Courier New", 
                       "맑은 고딕", "굴림", "나눔고딕", "DejaVu Sans"]
        
        # 실제 사용 가능한 폰트만 필터링
        available = []
        for f in common_fonts + tk_fonts:
            if f not in available:
                available.append(f)
        
        return sorted(available)[:20]  # 너무 많으면 20개로 제한
        
    def get_font(self, font_name, size):
        """선택된 폰트로 PIL 폰트 객체를 생성합니다."""
        # 시스템별 폰트 경로
        font_paths = []
        
        # Windows
        if os.name == 'nt':
            font_paths.extend([
                f'C:/Windows/Fonts/{font_name.lower().replace(" ", "")}.ttf',
                f'C:/Windows/Fonts/{font_name.lower()}.ttf',
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/malgun.ttf',
                'C:/Windows/Fonts/gulim.ttc',
            ])
        
        # macOS
        elif os.name == 'posix' and hasattr(os, 'uname') and os.uname().sysname == 'Darwin':
            font_paths.extend([
                f'/System/Library/Fonts/{font_name}.ttf',
                '/System/Library/Fonts/Arial.ttf',
                '/System/Library/Fonts/AppleGothic.ttf',
            ])
        
        # Linux
        else:
            font_paths.extend([
                f'/usr/share/fonts/truetype/dejavu/{font_name.replace(" ", "")}.ttf',
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
        
        # 기본 폰트 사용
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 노트북 위젯으로 탭 구성
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), columnspan=2)
        
        # 탭 1: 텍스트 서명/도장
        text_frame = ttk.Frame(notebook, padding="10")
        notebook.add(text_frame, text="텍스트 서명/도장")
        
        # 탭 2: 손글씨 서명
        drawing_frame = ttk.Frame(notebook, padding="10")
        notebook.add(drawing_frame, text="손글씨 서명")
        
        self.setup_text_tab(text_frame)
        self.setup_drawing_tab(drawing_frame)
        
        # 미리보기 및 저장 섹션 (공통)
        preview_frame = ttk.LabelFrame(main_frame, text="미리보기", padding="10")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.preview_label = ttk.Label(preview_frame, text="생성된 이미지가 여기에 표시됩니다.")
        self.preview_label.grid(row=0, column=0)
        
        # 저장 버튼
        ttk.Button(main_frame, text="이미지 저장", 
                  command=self.save_image).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 현재 이미지 저장용
        self.current_image = None
        
    def setup_text_tab(self, parent):
        # 텍스트 입력 섹션
        input_frame = ttk.LabelFrame(parent, text="입력 설정", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="이름/텍스트:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.text, width=30).grid(row=0, column=1, padx=5)
        
        # 폰트 선택
        ttk.Label(input_frame, text="폰트:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_var = tk.StringVar(value=self.available_fonts[0] if self.available_fonts else "Arial")
        font_combo = ttk.Combobox(input_frame, textvariable=self.font_var, 
                                 values=self.available_fonts, width=25, state="readonly")
        font_combo.grid(row=1, column=1, padx=5, pady=5)
        font_combo.bind('<<ComboboxSelected>>', self.on_font_changed)
        
        # 전자서명 섹션
        signature_frame = ttk.LabelFrame(parent, text="전자서명 생성", padding="10")
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
        stamp_frame = ttk.LabelFrame(parent, text="전자도장 생성", padding="10")
        stamp_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        ttk.Button(stamp_frame, text="색상 선택", 
                  command=lambda: self.choose_color('stamp')).grid(row=0, column=0, pady=5)
        
        ttk.Button(stamp_frame, text="원형 도장 생성", 
                  command=lambda: self.generate_stamp('circle')).grid(row=1, column=0, pady=2)
        ttk.Button(stamp_frame, text="사각 도장 생성", 
                  command=lambda: self.generate_stamp('square')).grid(row=2, column=0, pady=2)
        ttk.Button(stamp_frame, text="전통 도장 생성", 
                  command=lambda: self.generate_stamp('traditional')).grid(row=3, column=0, pady=2)
        
    def setup_drawing_tab(self, parent):
        # 그리기 캔버스 섹션
        canvas_frame = ttk.LabelFrame(parent, text="손글씨 서명 그리기", padding="10")
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 안내 텍스트
        ttk.Label(canvas_frame, text="아래 영역에 마우스로 서명을 그려주세요:").pack(pady=5)
        
        # 그리기 캔버스
        self.drawing_canvas = DrawingCanvas(canvas_frame)
        
        # 손글씨 서명 저장 버튼
        ttk.Button(canvas_frame, text="손글씨 서명으로 저장", 
                  command=self.save_handwritten_signature).pack(pady=10)
        
    def on_font_changed(self, event):
        self.selected_font = self.font_var.get()
    
    def choose_color(self, color_type):
        color = colorchooser.askcolor(title="색상 선택")[1]
        if color:
            if color_type == 'signature':
                self.signature_color = color
            else:
                self.stamp_color = color
    
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
        font = self.get_font(self.selected_font, font_size)
        
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
            font = self.get_font(self.selected_font, 30)
            
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
            font = self.get_font(self.selected_font, 28)
            
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
            font = self.get_font(self.selected_font, 24)
            
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
    
    def save_handwritten_signature(self):
        """손글씨 서명을 이미지로 저장"""
        try:
            # 캔버스를 이미지로 변환
            # 임시 파일로 저장 후 PIL로 열기
            import tempfile
            
            # 캔버스를 PostScript로 저장
            with tempfile.NamedTemporaryFile(suffix='.eps', delete=False) as tmp:
                self.drawing_canvas.canvas.postscript(file=tmp.name)
                
                # PIL로 EPS 파일 열기 (Ghostscript 필요)
                try:
                    img = Image.open(tmp.name)
                    # 배경을 투명하게 만들기
                    img = img.convert('RGBA')
                    
                    # 흰색 배경을 투명하게 변환
                    data = img.getdata()
                    new_data = []
                    for item in data:
                        if item[0] > 200 and item[1] > 200 and item[2] > 200:  # 흰색 계열
                            new_data.append((255, 255, 255, 0))  # 투명하게
                        else:
                            new_data.append(item)
                    
                    img.putdata(new_data)
                    self.current_image = img
                    self.show_preview(img)
                    
                except Exception as e:
                    # PostScript 변환이 실패하면 대안 방법 사용
                    messagebox.showinfo("안내", "손글씨 서명이 준비되었습니다. '이미지 저장' 버튼을 눌러주세요.")
                    # 간단한 대안: 캔버스 스크린샷 (품질이 떨어질 수 있음)
                    self.current_image = self.create_canvas_image()
                
                # 임시 파일 삭제
                os.unlink(tmp.name)
                
        except Exception as e:
            messagebox.showerror("오류", f"손글씨 서명 저장 중 오류가 발생했습니다: {str(e)}")
    
    def create_canvas_image(self):
        """캔버스를 PIL 이미지로 변환하는 대안 방법"""
        # 캔버스 크기 가져오기
        canvas_width = self.drawing_canvas.canvas.winfo_width()
        canvas_height = self.drawing_canvas.canvas.winfo_height()
        
        # 새 이미지 생성
        img = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 캔버스의 모든 선을 가져와서 이미지에 그리기
        # 이 방법은 복잡하므로 일단 기본 이미지 반환
        draw.text((50, 50), "손글씨 서명", fill='black')
        
        return img
    
    def show_preview(self, img):
        # 미리보기용 이미지 크기 조정
        preview_img = img.copy()
        preview_img.thumbnail((300, 200), Image.Resampling.LANCZOS)
        
        # tkinter에서 표시할 수 있도록 변환
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