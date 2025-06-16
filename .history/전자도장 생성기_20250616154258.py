import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk, ImageFilter
import os
import random
import math

class DrawableStampMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("직접 그리는 도장 생성기")
        self.root.geometry("1200x800")
        self.root.minsize(1100, 750)
        
        # 도장 설정 변수들
        self.stamp_size_var = tk.IntVar(value=300)
        self.border_type_var = tk.StringVar(value="사각형")
        self.border_thickness_var = tk.IntVar(value=8)  # 기본값 8로 변경
        self.grid_type_var = tk.StringVar(value="2x2")
        self.show_grid_var = tk.BooleanVar(value=True)
        self.stamp_color_var = tk.StringVar(value="#CC0000")
        
        # 도장 효과 변수 추가
        self.stamp_effect_var = tk.StringVar(value="기본")
        
        # 그리기 관련 변수
        self.pen_width = 14  # 기본값 14로 변경
        self.pen_color = '#CC0000'
        self.old_x = None
        self.old_y = None
        self.drawn_lines = []
        
        # 한글 그리드 텍스트 저장
        self.grid_texts = {}
        
        self.current_image = None
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="직접 그리는 도장 생성기", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 좌우 분할
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 설정 패널
        settings_frame = ttk.LabelFrame(content_frame, text="도장 설정", padding="10", width=300)
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        settings_frame.pack_propagate(False)
        
        # 오른쪽: 그리기 영역
        drawing_frame = ttk.LabelFrame(content_frame, text="도장 그리기 영역", padding="10")
        drawing_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_settings_panel(settings_frame)
        self.setup_drawing_panel(drawing_frame)
        
    def setup_settings_panel(self, parent):
        # 도장 크기
        size_frame = ttk.LabelFrame(parent, text="도장 크기", padding="5")
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="크기:").pack(anchor=tk.W)
        size_scale = ttk.Scale(size_frame, from_=200, to=500, variable=self.stamp_size_var,
                              orient=tk.HORIZONTAL, command=self.update_canvas_size)
        size_scale.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, textvariable=self.stamp_size_var).pack()
        
        # 외부 테두리
        border_frame = ttk.LabelFrame(parent, text="외부 테두리", padding="5")
        border_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(border_frame, text="모양:").pack(anchor=tk.W)
        border_combo = ttk.Combobox(border_frame, textvariable=self.border_type_var,
                                   values=["사각형", "원형", "둥근사각형", "없음"], 
                                   state="readonly", width=20)
        border_combo.pack(fill=tk.X, pady=2)
        border_combo.bind('<<ComboboxSelected>>', self.update_guides)
        
        ttk.Label(border_frame, text="두께:").pack(anchor=tk.W)
        border_scale = ttk.Scale(border_frame, from_=1, to=20, variable=self.border_thickness_var,
                                orient=tk.HORIZONTAL, command=self.update_guides)
        border_scale.pack(fill=tk.X, pady=2)
        ttk.Label(border_frame, textvariable=self.border_thickness_var).pack()
        
        # 가이드 그리드 (개선됨)
        grid_frame = ttk.LabelFrame(parent, text="가이드 그리드", padding="5")
        grid_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(grid_frame, text="가이드 표시", 
                       variable=self.show_grid_var, command=self.update_guides).pack(anchor=tk.W)
        
        ttk.Label(grid_frame, text="그리드 유형:").pack(anchor=tk.W)
        grid_combo = ttk.Combobox(grid_frame, textvariable=self.grid_type_var,
                                 values=["없음", "1x1", "1x2", "2x1", "2x2", "1x3", "3x1", 
                                        "2x3", "3x2", "1x4", "4x1", "2x4", "4x2",
                                        "한글세로", "한글가로"], 
                                 state="readonly", width=20)
        grid_combo.pack(fill=tk.X, pady=2)
        grid_combo.bind('<<ComboboxSelected>>', self.update_guides)
        
        # 한글 그리드 텍스트 입력
        self.text_input_frame = ttk.Frame(grid_frame)
        self.text_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.text_input_frame, text="한글 입력:").pack(anchor=tk.W)
        self.korean_text_var = tk.StringVar()
        self.korean_entry = ttk.Entry(self.text_input_frame, textvariable=self.korean_text_var)
        self.korean_entry.pack(fill=tk.X, pady=2)
        self.korean_entry.bind('<KeyRelease>', self.update_korean_grid)
        
        ttk.Button(self.text_input_frame, text="텍스트 지우기", 
                  command=self.clear_grid_text).pack(fill=tk.X, pady=2)
        
        # 도장 효과 (새로 추가)
        effect_frame = ttk.LabelFrame(parent, text="도장 효과", padding="5")
        effect_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(effect_frame, text="효과 유형:").pack(anchor=tk.W)
        effect_combo = ttk.Combobox(effect_frame, textvariable=self.stamp_effect_var,
                                   values=["기본", "도장효과", "거친효과", "흐린효과", "점선효과"], 
                                   state="readonly", width=20)
        effect_combo.pack(fill=tk.X, pady=2)
        
        # 그리기 도구
        pen_frame = ttk.LabelFrame(parent, text="그리기 도구", padding="5")
        pen_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(pen_frame, text="펜 색상", command=self.choose_pen_color).pack(fill=tk.X, pady=2)
        self.pen_color_display = tk.Label(pen_frame, bg=self.pen_color, 
                                         height=1, relief=tk.SUNKEN)
        self.pen_color_display.pack(fill=tk.X, pady=2)
        
        ttk.Label(pen_frame, text="펜 굵기:").pack(anchor=tk.W)
        self.pen_width_var = tk.IntVar(value=14)  # 기본값 14로 변경
        pen_scale = ttk.Scale(pen_frame, from_=1, to=30, variable=self.pen_width_var,
                             orient=tk.HORIZONTAL, command=self.update_pen_width)
        pen_scale.pack(fill=tk.X, pady=2)
        ttk.Label(pen_frame, textvariable=self.pen_width_var).pack()
        
        # 도장 색상 (최종 출력용)
        stamp_color_frame = ttk.LabelFrame(parent, text="최종 도장 색상", padding="5")
        stamp_color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(stamp_color_frame, text="도장 색상 선택", command=self.choose_stamp_color).pack(fill=tk.X, pady=2)
        self.stamp_color_display = tk.Label(stamp_color_frame, bg=self.stamp_color_var.get(), 
                                           height=2, relief=tk.SUNKEN)
        self.stamp_color_display.pack(fill=tk.X, pady=2)
        
        # 도구 버튼들
        tools_frame = ttk.LabelFrame(parent, text="도구", padding="5")
        tools_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(tools_frame, text="전체 지우기", command=self.clear_canvas).pack(fill=tk.X, pady=2)
        ttk.Button(tools_frame, text="가이드만 토글", command=self.toggle_guides).pack(fill=tk.X, pady=2)
        ttk.Button(tools_frame, text="미리보기 생성", command=self.generate_preview).pack(fill=tk.X, pady=2)
        ttk.Button(tools_frame, text="이미지 저장", command=self.save_image).pack(fill=tk.X, pady=2)
        
    def setup_drawing_panel(self, parent):
        # 안내 문구
        info_label = ttk.Label(parent, text="마우스로 직접 도장을 그려보세요. 가이드 라인을 참고하여 그리시면 됩니다.", 
                              font=('Arial', 10))
        info_label.pack(pady=(0, 10))
        
        # 캔버스 프레임 (중앙 정렬용)
        canvas_container = ttk.Frame(parent)
        canvas_container.pack(expand=True)
        
        # 그리기 캔버스
        size = self.stamp_size_var.get()
        self.drawing_canvas = tk.Canvas(canvas_container, width=size, height=size, 
                                       bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.drawing_canvas.pack()
        
        # 마우스 이벤트 바인딩
        self.drawing_canvas.bind('<B1-Motion>', self.paint)
        self.drawing_canvas.bind('<ButtonPress-1>', self.paint)
        self.drawing_canvas.bind('<ButtonRelease-1>', self.reset)
        
        # 미리보기 영역
        preview_label = ttk.Label(parent, text="최종 미리보기", font=('Arial', 12, 'bold'))
        preview_label.pack(pady=(20, 5))
        
        self.preview_canvas = tk.Canvas(parent, width=200, height=200, 
                                       bg='white', relief=tk.SUNKEN, borderwidth=1)
        self.preview_canvas.pack()
        
        # 초기 가이드 그리기
        self.update_guides()
        
    def update_canvas_size(self, event=None):
        """캔버스 크기 업데이트"""
        size = self.stamp_size_var.get()
        self.drawing_canvas.config(width=size, height=size)
        self.clear_canvas()
        self.update_guides()
        
    def update_guides(self, event=None):
        """가이드 라인 업데이트"""
        # 기존 가이드 제거
        self.drawing_canvas.delete("guide")
        self.drawing_canvas.delete("text_guide")
        
        if not self.show_grid_var.get():
            return
            
        size = self.stamp_size_var.get()
        border_type = self.border_type_var.get()
        border_thickness = self.border_thickness_var.get()
        grid_type = self.grid_type_var.get()
        
        guide_color = "#CCCCCC"
        
        # 외부 테두리 가이드
        if border_type != "없음":
            margin = 10
            if border_type == "사각형":
                self.drawing_canvas.create_rectangle(margin, margin, size-margin, size-margin,
                                                   outline=guide_color, width=border_thickness, tags="guide")
            elif border_type == "원형":
                self.drawing_canvas.create_oval(margin, margin, size-margin, size-margin,
                                               outline=guide_color, width=border_thickness, tags="guide")
            elif border_type == "둥근사각형":
                corner = 20
                points = [
                    margin+corner, margin,
                    size-margin-corner, margin,
                    size-margin, margin+corner,
                    size-margin, size-margin-corner,
                    size-margin-corner, size-margin,
                    margin+corner, size-margin,
                    margin, size-margin-corner,
                    margin, margin+corner,
                    margin+corner, margin
                ]
                self.drawing_canvas.create_line(points, outline=guide_color, 
                                              width=border_thickness, tags="guide", smooth=True)
        
        # 그리드 가이드
        self.draw_grid_guides(size, grid_type, guide_color)
    
    def draw_grid_guides(self, size, grid_type, guide_color):
        """그리드 가이드 그리기"""
        if grid_type == "없음":
            return
        
        margin = 25
        grid_width = size - 2 * margin
        grid_height = size - 2 * margin
        
        if grid_type in ["한글세로", "한글가로"]:
            self.draw_korean_grid(size, grid_type, guide_color, margin)
        else:
            rows, cols = map(int, grid_type.split('x'))
            cell_width = grid_width / cols
            cell_height = grid_height / rows
            
            # 세로 선
            for i in range(1, cols):
                x = margin + i * cell_width
                self.drawing_canvas.create_line(x, margin, x, size-margin, 
                                              fill=guide_color, width=1, tags="guide")
            
            # 가로 선
            for i in range(1, rows):
                y = margin + i * cell_height
                self.drawing_canvas.create_line(margin, y, size-margin, y, 
                                              fill=guide_color, width=1, tags="guide")
    
    def draw_korean_grid(self, size, grid_type, guide_color, margin):
        """한글 그리드 그리기"""
        text = self.korean_text_var.get()
        if not text:
            return
        
        grid_width = size - 2 * margin
        grid_height = size - 2 * margin
        
        if grid_type == "한글세로":
            # 세로쓰기: 오른쪽에서 왼쪽으로, 위에서 아래로
            char_count = len(text)
            if char_count > 0:
                char_width = grid_width / char_count
                char_height = grid_height / 5  # 한 글자당 5칸 정도
                
                for i in range(char_count):
                    char = text[i]
                    x = size - margin - (i + 1) * char_width + char_width/2
                    y = margin + char_height * 2
                    
                    self.drawing_canvas.create_text(x, y, text=char, font=("Arial", 20), 
                                                  fill=guide_color, tags="text_guide")
                    
                    # 글자 영역 표시
                    x1 = size - margin - (i + 1) * char_width
                    x2 = size - margin - i * char_width
                    self.drawing_canvas.create_rectangle(x1, margin, x2, size-margin,
                                                       outline=guide_color, width=1, tags="guide")
        
        elif grid_type == "한글가로":
            # 가로쓰기: 왼쪽에서 오른쪽으로
            char_count = len(text)
            if char_count > 0:
                char_width = grid_width / char_count
                
                for i in range(char_count):
                    char = text[i]
                    x = margin + i * char_width + char_width/2
                    y = size/2
                    
                    self.drawing_canvas.create_text(x, y, text=char, font=("Arial", 20), 
                                                  fill=guide_color, tags="text_guide")
                    
                    # 글자 영역 표시
                    if i > 0:
                        x_line = margin + i * char_width
                        self.drawing_canvas.create_line(x_line, margin, x_line, size-margin,
                                                      fill=guide_color, width=1, tags="guide")
    
    def update_korean_grid(self, event=None):
        """한글 그리드 업데이트"""
        if self.grid_type_var.get() in ["한글세로", "한글가로"]:
            self.update_guides()
    
    def clear_grid_text(self):
        """그리드 텍스트 지우기"""
        self.korean_text_var.set("")
        self.update_guides()
    
    def choose_pen_color(self):
        """펜 색상 선택"""
        color = colorchooser.askcolor(title="펜 색상 선택")[1]
        if color:
            self.pen_color = color
            self.pen_color_display.config(bg=color)
    
    def choose_stamp_color(self):
        """최종 도장 색상 선택"""
        color = colorchooser.askcolor(title="도장 색상 선택")[1]
        if color:
            self.stamp_color_var.set(color)
            self.stamp_color_display.config(bg=color)
    
    def update_pen_width(self, event=None):
        """펜 굵기 업데이트"""
        self.pen_width = self.pen_width_var.get()
    
    def paint(self, event):
        """그리기 함수"""
        if self.old_x and self.old_y:
            line_id = self.drawing_canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                                    width=self.pen_width, fill=self.pen_color,
                                                    capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawing")
            # 선 정보 저장
            self.drawn_lines.append({
                'coords': [self.old_x, self.old_y, event.x, event.y],
                'width': self.pen_width,
                'color': self.pen_color
            })
        self.old_x = event.x
        self.old_y = event.y
    
    def reset(self, event):
        """마우스 버튼 해제"""
        self.old_x = None
        self.old_y = None
    
    def clear_canvas(self):
        """전체 지우기"""
        self.drawing_canvas.delete("drawing")
        self.drawn_lines = []
        self.preview_canvas.delete("all")
        messagebox.showinfo("완료", "캔버스가 지워졌습니다.")
    
    def toggle_guides(self):
        """가이드만 토글"""
        self.show_grid_var.set(not self.show_grid_var.get())
        self.update_guides()
    
    def generate_preview(self):
        """최종 미리보기 생성"""
        try:
            if not self.drawn_lines:
                messagebox.showwarning("경고", "먼저 도장을 그려주세요.")
                return
            
            # 도장 이미지 생성
            self.current_image = self.create_stamp_image()
            
            if self.current_image:
                # 미리보기 캔버스에 표시
                self.display_preview()
                messagebox.showinfo("완료", "미리보기가 생성되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"미리보기 생성 중 오류가 발생했습니다:\n{str(e)}")
    
    def create_stamp_image(self):
        """최종 도장 이미지 생성"""
        size = self.stamp_size_var.get()
        final_color = self.stamp_color_var.get()
        effect = self.stamp_effect_var.get()
        
        # 이미지 생성
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 외부 테두리 그리기
        self.draw_border(draw, size, final_color)
        
        # 그려진 선들을 최종 색상으로 그리기
        for line in self.drawn_lines:
            coords = line['coords']
            width = line['width']
            
            # 효과에 따른 선 그리기
            if effect == "기본":
                self.draw_basic_line(draw, coords, width, final_color)
            elif effect == "도장효과":
                self.draw_stamp_effect_line(draw, coords, width, final_color)
            elif effect == "거친효과":
                self.draw_rough_line(draw, coords, width, final_color)
            elif effect == "흐린효과":
                self.draw_blur_line(draw, coords, width, final_color)
            elif effect == "점선효과":
                self.draw_dotted_line(draw, coords, width, final_color)
        
        # 효과별 후처리
        if effect == "흐린효과":
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
        elif effect == "도장효과":
            img = self.apply_stamp_texture(img)
        
        return img
    
    def draw_basic_line(self, draw, coords, width, color):
        """기본 선 그리기"""
        draw.line(coords, fill=color, width=width)
        x1, y1, x2, y2 = coords
        radius = width // 2
        draw.ellipse([x1-radius, y1-radius, x1+radius, y1+radius], fill=color)
        draw.ellipse([x2-radius, y2-radius, x2+radius, y2+radius], fill=color)
    
    def draw_stamp_effect_line(self, draw, coords, width, color):
        """도장 효과 선 그리기"""
        x1, y1, x2, y2 = coords
        # 불규칙한 점들로 선 표현
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if distance > 0:
            steps = int(distance / 2)
            for i in range(steps):
                t = i / steps if steps > 1 else 0
                x = int(x1 + t * (x2 - x1) + random.randint(-2, 2))
                y = int(y1 + t * (y2 - y1) + random.randint(-2, 2))
                radius = random.randint(width//3, width//2)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    def draw_rough_line(self, draw, coords, width, color):
        """거친 효과 선 그리기"""
        x1, y1, x2, y2 = coords
        # 여러 개의 가는 선으로 두꺼운 선 표현
        for i in range(width):
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            draw.line([x1+offset_x, y1+offset_y, x2+offset_x, y2+offset_y], 
                     fill=color, width=1)
    
    def draw_blur_line(self, draw, coords, width, color):
        """흐린 효과 선 그리기"""
        # 여러 번 겹쳐서 그려서 흐린 효과
        for i in range(3):
            alpha = 100 - i * 20
            blur_color = color + format(alpha, '02x') if len(color) == 7 else color
            offset = i
            x1, y1, x2, y2 = coords
            draw.line([x1+offset, y1+offset, x2+offset, y2+offset], 
                     fill=color, width=width+i)
    
    def draw_dotted_line(self, draw, coords, width, color):
        """점선 효과 선 그리기"""
        x1, y1, x2, y2 = coords
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if distance > 0:
            dot_spacing = width * 2
            dots = int(distance / dot_spacing)
            for i in range(dots):
                t = i / dots if dots > 1 else 0
                x = int(x1 + t * (x2 - x1))
                y = int(y1 + t * (y2 - y1))
                radius = width // 2
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    def apply_stamp_texture(self, img):
        """도장 텍스처 효과 적용"""
        # 노이즈 추가하여 실제 도장처럼 보이게 함
        width, height = img.size
        pixels = img.load()
        
        for y in range(height):
            for x in range(width):
                if pixels[x, y][3] > 0:  # 투명하지 않은 픽셀만
                    # 랜덤하게 일부 픽셀을 투명하게 만들어 텍스처 효과
                    if random.random() < 0.1:
                        pixels[x, y] = (pixels[x, y][0], pixels[x, y][1], 
                                       pixels[x, y][2], int(pixels[x, y][3] * 0.5))
        
        return img
    
    def draw_border(self, draw, size, color):
        """외부 테두리 그리기"""
        border_type = self.border_type_var.get()
        thickness = self.border_thickness_var.get()
        margin = 10
        
        if border_type == "없음":
            return
        
        if border_type == "사각형":
            draw.rectangle([margin, margin, size-margin, size-margin], 
                          outline=color, width=thickness)
        elif border_type == "원형":
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        outline=color, width=thickness)
        elif border_type == "둥근사각형":
            corner_radius = 20
            # PIL의 rounded_rectangle 사용 (Pillow 8.2.0+)
            try:
                draw.rounded_rectangle([margin, margin, size-margin, size-margin], 
                                      radius=corner_radius, outline=color, width=thickness)
            except AttributeError:
                # 구버전 Pillow에서는 일반 사각형으로 대체
                draw.rectangle([margin, margin, size-margin, size-margin], 
                              outline=color, width=thickness)
    
    def display_preview(self):
        """미리보기 캔버스에 표시"""
        if self.current_image:
            # 미리보기 크기로 조정
            preview_img = self.current_image.copy()
            preview_img.thumbnail((180, 180), Image.Resampling.LANCZOS)
            
            # tkinter 이미지로 변환
            photo = ImageTk.PhotoImage(preview_img)
            
            # 미리보기 캔버스 지우고 표시
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(100, 100, image=photo)
            self.preview_canvas.image = photo
    
    def save_image(self):
        """이미지 저장"""
        if self.current_image is None:
            messagebox.showwarning("경고", "먼저 '미리보기 생성' 버튼을 눌러주세요.")
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
                    background = Image.new('RGB', self.current_image.size, (255, 255, 255))
                    background.paste(self.current_image, mask=self.current_image.split()[3])
                    background.save(filename, quality=95)
                else:
                    self.current_image.save(filename)
                
                messagebox.showinfo("저장 완료", f"도장이 저장되었습니다:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("저장 실패", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")

def main():
    root = tk.Tk()
    app = DrawableStampMaker(root)
    root.mainloop()

if __name__ == "__main__":
    main()