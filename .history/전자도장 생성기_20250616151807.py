import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk
import math
import os

class ElectronicStampMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("전자 도장 생성기")
        self.root.geometry("800x700")
        self.root.minsize(750, 650)
        
        # 도장 설정 변수들
        self.text_var = tk.StringVar(value="홍길동")
        self.stamp_size_var = tk.IntVar(value=150)
        self.circle_count_var = tk.IntVar(value=2)
        self.outer_thickness_var = tk.IntVar(value=3)
        self.inner_thickness_var = tk.IntVar(value=2)
        self.text_layout_var = tk.StringVar(value="세로")
        self.text_curve_var = tk.BooleanVar(value=False)
        self.text_size_var = tk.IntVar(value=30)
        self.stamp_color_var = tk.StringVar(value="#CC0000")
        
        self.current_image = None
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="전자 도장 생성기", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 좌우 분할
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽 설정 패널
        settings_frame = ttk.LabelFrame(content_frame, text="도장 설정", padding="10")
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.setup_settings_panel(settings_frame)
        
        # 오른쪽 미리보기 패널
        preview_frame = ttk.LabelFrame(content_frame, text="미리보기", padding="10")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_preview_panel(preview_frame)
        
    def setup_settings_panel(self, parent):
        # 텍스트 입력
        text_frame = ttk.LabelFrame(parent, text="도장 텍스트", padding="5")
        text_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_frame, text="이름:").pack(anchor=tk.W)
        ttk.Entry(text_frame, textvariable=self.text_var, width=15).pack(fill=tk.X, pady=2)
        
        # 도장 크기
        size_frame = ttk.LabelFrame(parent, text="도장 크기", padding="5")
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="크기:").pack(anchor=tk.W)
        size_scale = ttk.Scale(size_frame, from_=100, to=300, variable=self.stamp_size_var,
                              orient=tk.HORIZONTAL)
        size_scale.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, textvariable=self.stamp_size_var).pack()
        
        # 원 설정
        circle_frame = ttk.LabelFrame(parent, text="원 설정", padding="5")
        circle_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(circle_frame, text="원 개수:").pack(anchor=tk.W)
        circle_combo = ttk.Combobox(circle_frame, textvariable=self.circle_count_var,
                                   values=[1, 2, 3], state="readonly", width=12)
        circle_combo.pack(fill=tk.X, pady=2)
        
        ttk.Label(circle_frame, text="바깥 원 두께:").pack(anchor=tk.W)
        outer_scale = ttk.Scale(circle_frame, from_=1, to=10, variable=self.outer_thickness_var,
                               orient=tk.HORIZONTAL)
        outer_scale.pack(fill=tk.X, pady=2)
        ttk.Label(circle_frame, textvariable=self.outer_thickness_var).pack()
        
        ttk.Label(circle_frame, text="안쪽 원 두께:").pack(anchor=tk.W)
        inner_scale = ttk.Scale(circle_frame, from_=1, to=8, variable=self.inner_thickness_var,
                               orient=tk.HORIZONTAL)
        inner_scale.pack(fill=tk.X, pady=2)
        ttk.Label(circle_frame, textvariable=self.inner_thickness_var).pack()
        
        # 텍스트 배치
        layout_frame = ttk.LabelFrame(parent, text="텍스트 배치", padding="5")
        layout_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(layout_frame, text="배치 방식:").pack(anchor=tk.W)
        layout_combo = ttk.Combobox(layout_frame, textvariable=self.text_layout_var,
                                   values=["세로", "가로", "원형"], state="readonly", width=12)
        layout_combo.pack(fill=tk.X, pady=2)
        
        ttk.Checkbutton(layout_frame, text="원에 맞춰 휘기", 
                       variable=self.text_curve_var).pack(anchor=tk.W, pady=2)
        
        ttk.Label(layout_frame, text="글자 크기:").pack(anchor=tk.W)
        text_size_scale = ttk.Scale(layout_frame, from_=15, to=60, variable=self.text_size_var,
                                   orient=tk.HORIZONTAL)
        text_size_scale.pack(fill=tk.X, pady=2)
        ttk.Label(layout_frame, textvariable=self.text_size_var).pack()
        
        # 색상 설정
        color_frame = ttk.LabelFrame(parent, text="색상", padding="5")
        color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(color_frame, text="색상 선택", command=self.choose_color).pack(fill=tk.X, pady=2)
        self.color_display = tk.Label(color_frame, bg=self.stamp_color_var.get(), 
                                     height=2, relief=tk.SUNKEN)
        self.color_display.pack(fill=tk.X, pady=2)
        
        # 버튼들
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="미리보기 생성", 
                  command=self.generate_preview).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="이미지 저장", 
                  command=self.save_image).pack(fill=tk.X, pady=2)
        
        # 실시간 업데이트 바인딩
        self.bind_realtime_updates()
        
    def setup_preview_panel(self, parent):
        # 미리보기 캔버스
        self.preview_canvas = tk.Canvas(parent, width=400, height=400, 
                                       bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.preview_canvas.pack(expand=True, pady=20)
        
        # 안내 텍스트
        self.preview_canvas.create_text(200, 200, text="설정을 조정하면\n자동으로 미리보기가 생성됩니다", 
                                       fill='gray', font=('Arial', 12), justify=tk.CENTER)
        
    def bind_realtime_updates(self):
        """실시간 업데이트를 위한 이벤트 바인딩"""
        # 변수 변경 시 자동 업데이트
        self.text_var.trace_add('write', self.on_setting_change)
        self.stamp_size_var.trace_add('write', self.on_setting_change)
        self.circle_count_var.trace_add('write', self.on_setting_change)
        self.outer_thickness_var.trace_add('write', self.on_setting_change)
        self.inner_thickness_var.trace_add('write', self.on_setting_change)
        self.text_layout_var.trace_add('write', self.on_setting_change)
        self.text_curve_var.trace_add('write', self.on_setting_change)
        self.text_size_var.trace_add('write', self.on_setting_change)
        
    def on_setting_change(self, *args):
        """설정 변경 시 자동으로 미리보기 업데이트"""
        self.root.after(50, self.generate_preview)  # 약간의 지연을 두고 업데이트
        
    def choose_color(self):
        """색상 선택"""
        color = colorchooser.askcolor(title="도장 색상 선택")[1]
        if color:
            self.stamp_color_var.set(color)
            self.color_display.config(bg=color)
            self.generate_preview()
            
    def generate_preview(self):
        """도장 미리보기 생성"""
        try:
            # 캔버스 지우기
            self.preview_canvas.delete("all")
            
            # 도장 이미지 생성
            stamp_image = self.create_stamp_image()
            if stamp_image:
                self.current_image = stamp_image
                
                # 캔버스에 표시
                self.display_on_canvas(stamp_image)
            
        except Exception as e:
            print(f"미리보기 생성 오류: {e}")
            
    def create_stamp_image(self):
        """도장 이미지 생성"""
        size = self.stamp_size_var.get()
        text = self.text_var.get().strip()
        
        if not text:
            return None
            
        # 이미지 생성
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        center = size // 2
        color = self.stamp_color_var.get()
        
        # 원 그리기
        self.draw_circles(draw, center, size, color)
        
        # 텍스트 그리기
        self.draw_text(draw, center, size, text, color)
        
        return img
        
    def draw_circles(self, draw, center, size, color):
        """원 그리기"""
        circle_count = self.circle_count_var.get()
        outer_thickness = self.outer_thickness_var.get()
        inner_thickness = self.inner_thickness_var.get()
        
        # 바깥 원
        margin = 5
        outer_radius = center - margin
        draw.ellipse([center - outer_radius, center - outer_radius,
                     center + outer_radius, center + outer_radius],
                    outline=color, width=outer_thickness)
        
        if circle_count >= 2:
            # 안쪽 원
            inner_radius = outer_radius - 15
            draw.ellipse([center - inner_radius, center - inner_radius,
                         center + inner_radius, center + inner_radius],
                        outline=color, width=inner_thickness)
            
        if circle_count >= 3:
            # 가장 안쪽 원
            innermost_radius = inner_radius - 12
            draw.ellipse([center - innermost_radius, center - innermost_radius,
                         center + innermost_radius, center + innermost_radius],
                        outline=color, width=inner_thickness)
            
    def draw_text(self, draw, center, size, text, color):
        """텍스트 그리기"""
        layout = self.text_layout_var.get()
        text_size = self.text_size_var.get()
        curve = self.text_curve_var.get()
        
        # 폰트 설정
        try:
            font = ImageFont.truetype("malgun.ttf", text_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", text_size)
            except:
                font = ImageFont.load_default()
        
        if layout == "세로":
            self.draw_vertical_text(draw, center, text, font, color, curve, size)
        elif layout == "가로":
            self.draw_horizontal_text(draw, center, text, font, color, curve, size)
        elif layout == "원형":
            self.draw_circular_text(draw, center, text, font, color, size)
            
    def draw_vertical_text(self, draw, center, text, font, color, curve, size):
        """세로 텍스트 그리기"""
        if curve and len(text) > 2:
            # 원에 맞춰 휘어진 세로 텍스트
            radius = size // 3
            angle_step = 0.8  # 글자 간 각도
            start_angle = -math.pi/2 - (len(text)-1) * angle_step / 2
            
            for i, char in enumerate(text):
                angle = start_angle + i * angle_step
                x = center + radius * math.cos(angle)
                y = center + radius * math.sin(angle)
                
                # 글자 회전 각도 계산
                rotation_angle = math.degrees(angle + math.pi/2)
                
                # 임시 이미지에 회전된 글자 그리기
                char_img = Image.new('RGBA', (text_size*2, text_size*2), (255, 255, 255, 0))
                char_draw = ImageDraw.Draw(char_img)
                char_draw.text((text_size//2, text_size//2), char, font=font, fill=color, anchor="mm")
                
                # 글자 회전
                rotated_char = char_img.rotate(rotation_angle, expand=True)
                
                # 원본 이미지에 붙이기
                char_w, char_h = rotated_char.size
                paste_x = int(x - char_w//2)
                paste_y = int(y - char_h//2)
                
                # 이미지 생성 시 마스크 생성
                temp_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                temp_img.paste(rotated_char, (paste_x, paste_y), rotated_char)
                
                # 원본에 합성
                draw._image.paste(temp_img, (0, 0), temp_img)
        else:
            # 일반 세로 텍스트
            char_height = text_size + 5
            total_height = len(text) * char_height
            start_y = center - total_height // 2
            
            for i, char in enumerate(text):
                y = start_y + i * char_height
                draw.text((center, y), char, font=font, fill=color, anchor="mm")
                
    def draw_horizontal_text(self, draw, center, text, font, color, curve, size):
        """가로 텍스트 그리기"""
        if curve and len(text) > 2:
            # 원에 맞춰 휘어진 가로 텍스트
            radius = size // 4
            angle_step = 0.6
            start_angle = -math.pi/2 - (len(text)-1) * angle_step / 2
            
            for i, char in enumerate(text):
                angle = start_angle + i * angle_step
                x = center + radius * math.cos(angle)
                y = center + radius * math.sin(angle)
                draw.text((x, y), char, font=font, fill=color, anchor="mm")
        else:
            # 일반 가로 텍스트
            draw.text((center, center), text, font=font, fill=color, anchor="mm")
            
    def draw_circular_text(self, draw, center, text, font, color, size):
        """원형 텍스트 그리기"""
        radius = size // 3
        angle_step = 2 * math.pi / len(text)
        start_angle = -math.pi / 2
        
        for i, char in enumerate(text):
            angle = start_angle + i * angle_step
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            
            # 글자 회전 각도
            rotation_angle = math.degrees(angle + math.pi/2)
            
            # 회전된 글자 생성
            char_img = Image.new('RGBA', (text_size*2, text_size*2), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((text_size//2, text_size//2), char, font=font, fill=color, anchor="mm")
            
            rotated_char = char_img.rotate(rotation_angle, expand=True)
            
            # 붙이기
            char_w, char_h = rotated_char.size
            paste_x = int(x - char_w//2)
            paste_y = int(y - char_h//2)
            
            temp_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            temp_img.paste(rotated_char, (paste_x, paste_y), rotated_char)
            draw._image.paste(temp_img, (0, 0), temp_img)
            
    def display_on_canvas(self, img):
        """캔버스에 이미지 표시"""
        # 캔버스 크기에 맞게 조정
        display_img = img.copy()
        display_img.thumbnail((350, 350), Image.Resampling.LANCZOS)
        
        # tkinter 포토 이미지로 변환
        photo = ImageTk.PhotoImage(display_img)
        
        # 캔버스 중앙에 표시
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:  # 캔버스가 초기화된 경우
            x = canvas_width // 2
            y = canvas_height // 2
            self.preview_canvas.create_image(x, y, image=photo)
            self.preview_canvas.image = photo  # 참조 유지
            
    def save_image(self):
        """이미지 저장"""
        if self.current_image is None:
            messagebox.showwarning("경고", "먼저 도장을 생성해주세요.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="도장 이미지 저장",
            defaultextension=".png",
            filetypes=[
                ("PNG 파일", "*.png"),
                ("JPEG 파일", "*.jpg"),
                ("모든 파일", "*.*")
            ]
        )
        
        if filename:
            try:
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    # JPG는 투명도 미지원, 흰색 배경 추가
                    background = Image.new('RGB', self.current_image.size, (255, 255, 255))
                    background.paste(self.current_image, mask=self.current_image.split()[3])
                    background.save(filename, quality=95)
                else:
                    # PNG는 투명 배경 유지
                    self.current_image.save(filename)
                    
                messagebox.showinfo("저장 완료", f"도장이 저장되었습니다:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("저장 실패", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")

def main():
    root = tk.Tk()
    app = ElectronicStampMaker(root)
    root.mainloop()

if __name__ == "__main__":
    main()