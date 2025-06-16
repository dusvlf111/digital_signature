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
        # 외부 테두리
        border_frame = ttk.LabelFrame(parent, text="외부 테두리", padding="5")
        border_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(border_frame, text="모양:").pack(anchor=tk.W)
        border_combo = ttk.Combobox(border_frame, textvariable=self.border_type_var,
                                   values=["사각형", "원형", "타원형", "긴타원형", "둥근사각형", "없음"], 
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
                                        "한글십자"], 
                                 state="readonly", width=20)
        grid_combo.pack(fill=tk.X, pady=2)
        grid_combo.bind('<<ComboboxSelected>>', self.update_guides)
        
        # 도장 효과 (새로 추가)
        effect_frame = ttk.LabelFrame(parent, text="도장 효과", padding="5")
        effect_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(effect_frame, text="효과 유형:").pack(anchor=tk.W)
        effect_combo = ttk.Combobox(effect_frame, textvariable=self.stamp_effect_var,
                                   values=["기본", "거친효과"], 
                                   state="readonly", width=20)
        effect_combo.pack(fill=tk.X, pady=2)
        
        # 선 효과 설정 (새로 추가)
        line_frame = ttk.LabelFrame(parent, text="선 효과", padding="5")
        line_frame.pack(fill=tk.X, pady=5)
        
        # 선끝 모양
        ttk.Label(line_frame, text="선끝 모양:").pack(anchor=tk.W)
        self.line_cap_var = tk.StringVar(value="둥글게")
        cap_combo = ttk.Combobox(line_frame, textvariable=self.line_cap_var,
                                values=["둥글게", "뾰족하게", "평평하게"], 
                                state="readonly", width=20)
        cap_combo.pack(fill=tk.X, pady=2)
        
        # 획 굵기 변화
        self.random_width_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(line_frame, text="획마다 굵기 랜덤", 
                       variable=self.random_width_var).pack(anchor=tk.W, pady=2)
        
        # 양각/음각 효과
        ttk.Label(line_frame, text="조각 효과:").pack(anchor=tk.W)
        self.carving_var = tk.StringVar(value="없음")
        carving_combo = ttk.Combobox(line_frame, textvariable=self.carving_var,
                                    values=["없음", "양각", "음각"], 
                                    state="readonly", width=20)
        carving_combo.pack(fill=tk.X, pady=2)
        
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
        
        # 중요한 버튼들을 더 크게
        ttk.Button(tools_frame, text="🔍 미리보기 생성", command=self.generate_preview).pack(fill=tk.X, pady=3)
        ttk.Button(tools_frame, text="💾 이미지 저장", command=self.save_image).pack(fill=tk.X, pady=3)
        
    def setup_drawing_panel(self, parent):
        # 안내 문구
        info_label = ttk.Label(parent, text="마우스로 직접 도장을 그려보세요. 가이드 라인을 참고하여 그리시면 됩니다.", 
                              font=('Arial', 10))
        info_label.pack(pady=(0, 10))
        
        # 캔버스 프레임 (중앙 정렬용)
        canvas_container = ttk.Frame(parent)
        canvas_container.pack(expand=True)
        
        # 그리기 캔버스
        size = 300  # 고정 크기로 변경
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
        
    def update_guides(self, event=None):
        """가이드 라인 업데이트"""
        # 기존 가이드 제거
        self.drawing_canvas.delete("guide")
        self.drawing_canvas.delete("text_guide")
        
        if not self.show_grid_var.get():
            return
            
        size = 300  # 고정 크기
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
            elif border_type == "타원형":
                # 세로로 긴 타원
                self.drawing_canvas.create_oval(margin+20, margin, size-margin-20, size-margin,
                                               outline=guide_color, width=border_thickness, tags="guide")
            elif border_type == "긴타원형":
                # 더 긴 타원
                self.drawing_canvas.create_oval(margin+40, margin, size-margin-40, size-margin,
                                               outline=guide_color, width=border_thickness, tags="guide")
            elif border_type == "둥근사각형":
                # 둥근 사각형을 여러 개의 직선과 호로 근사
                corner = 20
                # 상단 가로선
                self.drawing_canvas.create_line(margin+corner, margin, size-margin-corner, margin,
                                              fill=guide_color, width=border_thickness, tags="guide")
                # 우측 세로선
                self.drawing_canvas.create_line(size-margin, margin+corner, size-margin, size-margin-corner,
                                              fill=guide_color, width=border_thickness, tags="guide")
                # 하단 가로선
                self.drawing_canvas.create_line(size-margin-corner, size-margin, margin+corner, size-margin,
                                              fill=guide_color, width=border_thickness, tags="guide")
                # 좌측 세로선
                self.drawing_canvas.create_line(margin, size-margin-corner, margin, margin+corner,
                                              fill=guide_color, width=border_thickness, tags="guide")
                # 모서리 호 (근사)
                self.drawing_canvas.create_arc(margin, margin, margin+corner*2, margin+corner*2,
                                             start=90, extent=90, outline=guide_color, width=border_thickness, tags="guide", style="arc")
                self.drawing_canvas.create_arc(size-margin-corner*2, margin, size-margin, margin+corner*2,
                                             start=0, extent=90, outline=guide_color, width=border_thickness, tags="guide", style="arc")
                self.drawing_canvas.create_arc(size-margin-corner*2, size-margin-corner*2, size-margin, size-margin,
                                             start=270, extent=90, outline=guide_color, width=border_thickness, tags="guide", style="arc")
                self.drawing_canvas.create_arc(margin, size-margin-corner*2, margin+corner*2, size-margin,
                                             start=180, extent=90, outline=guide_color, width=border_thickness, tags="guide", style="arc")
        
        # 그리드 가이드
        self.draw_grid_guides(size, grid_type, guide_color)
    
    def draw_grid_guides(self, size, grid_type, guide_color):
        """그리드 가이드 그리기"""
        if grid_type == "없음":
            return
        
        margin = 25
        grid_width = size - 2 * margin
        grid_height = size - 2 * margin
        
        if grid_type == "한글십자":
            self.draw_korean_cross_grid(size, guide_color, margin)
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
    
    def draw_korean_cross_grid(self, size, guide_color, margin):
        """한글 십자 점선 그리드 그리기"""
        grid_width = size - 2 * margin
        grid_height = size - 2 * margin
        
        # 각 칸의 크기 (2x2 기준)
        cell_width = grid_width / 2
        cell_height = grid_height / 2
        
        # 각 칸에 십자 점선 그리기
        for row in range(2):
            for col in range(2):
                # 칸의 중심점
                center_x = margin + col * cell_width + cell_width / 2
                center_y = margin + row * cell_height + cell_height / 2
                
                # 세로 점선 (십자의 세로 부분)
                y_start = margin + row * cell_height + 10
                y_end = margin + (row + 1) * cell_height - 10
                self.draw_dotted_guide_line(center_x, y_start, center_x, y_end, guide_color)
                
                # 가로 점선 (십자의 가로 부분)
                x_start = margin + col * cell_width + 10
                x_end = margin + (col + 1) * cell_width - 10
                self.draw_dotted_guide_line(x_start, center_y, x_end, center_y, guide_color)
        
        # 칸 구분선
        for i in range(1, 2):
            x = margin + i * cell_width
            self.drawing_canvas.create_line(x, margin, x, size-margin, 
                                          fill=guide_color, width=1, tags="guide")
        
        for i in range(1, 2):
            y = margin + i * cell_height
            self.drawing_canvas.create_line(margin, y, size-margin, y, 
                                          fill=guide_color, width=1, tags="guide")
    
    def draw_dotted_guide_line(self, x1, y1, x2, y2, color):
        """점선 가이드 라인 그리기"""
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        dash_length = 3
        gap_length = 3
        total_length = dash_length + gap_length
        
        if distance > 0:
            num_dashes = int(distance / total_length)
            for i in range(num_dashes):
                t1 = (i * total_length) / distance
                t2 = (i * total_length + dash_length) / distance
                
                if t2 > 1:
                    t2 = 1
                
                start_x = x1 + t1 * (x2 - x1)
                start_y = y1 + t1 * (y2 - y1)
                end_x = x1 + t2 * (x2 - x1)
                end_y = y1 + t2 * (y2 - y1)
                
                self.drawing_canvas.create_line(start_x, start_y, end_x, end_y,
                                              fill=color, width=1, tags="guide")
    
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
            # 랜덤 굵기 적용
            current_width = self.pen_width
            if self.random_width_var.get():
                # 기본 굵기의 70%~130% 범위에서 랜덤
                variation = random.uniform(0.7, 1.3)
                current_width = max(1, int(self.pen_width * variation))
            
            # 선끝 모양 설정
            cap_style = tk.ROUND  # 기본값
            if self.line_cap_var.get() == "뾰족하게":
                cap_style = tk.PROJECTING
            elif self.line_cap_var.get() == "평평하게":
                cap_style = tk.BUTT
            elif self.line_cap_var.get() == "둥글게":
                cap_style = tk.ROUND
            
            line_id = self.drawing_canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                                    width=current_width, fill=self.pen_color,
                                                    capstyle=cap_style, smooth=tk.TRUE, tags="drawing")
            # 선 정보 저장
            self.drawn_lines.append({
                'coords': [self.old_x, self.old_y, event.x, event.y],
                'width': current_width,
                'color': self.pen_color,
                'cap_style': self.line_cap_var.get()
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
        size = 300  # 고정 크기
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
            cap_style = line.get('cap_style', '둥글게')
            
            # 조각 효과에 따른 색상 조정
            line_color = final_color
            if self.carving_var.get() == "양각":
                line_color = self.lighten_color(final_color, 0.3)
            elif self.carving_var.get() == "음각":
                line_color = self.darken_color(final_color, 0.3)
            
            # 효과에 따른 선 그리기
            if effect == "기본":
                self.draw_basic_line(draw, coords, width, line_color, cap_style)
            elif effect == "거친효과":
                self.draw_rough_line(draw, coords, width, line_color, cap_style)
        
        # 조각 효과 후처리
        if self.carving_var.get() in ["양각", "음각"]:
            img = self.apply_carving_effect(img)
        
        return img
    
    def draw_basic_line(self, draw, coords, width, color, cap_style="둥글게"):
        """기본 선 그리기"""
        x1, y1, x2, y2 = coords
        
        # 선 그리기
        draw.line(coords, fill=color, width=width)
        
        # 선끝 처리
        if cap_style == "둥글게":
            radius = width // 2
            draw.ellipse([x1-radius, y1-radius, x1+radius, y1+radius], fill=color)
            draw.ellipse([x2-radius, y2-radius, x2+radius, y2+radius], fill=color)
        elif cap_style == "뾰족하게":
            # 뾰족한 끝을 위한 작은 삼각형 추가
            self.draw_pointed_cap(draw, x1, y1, x2, y2, width, color, True)
            self.draw_pointed_cap(draw, x2, y2, x1, y1, width, color, False)
        # 평평하게는 기본 선으로 충분
    
    def draw_pointed_cap(self, draw, cap_x, cap_y, other_x, other_y, width, color, is_start):
        """뾰족한 선끝 그리기"""
        # 선의 방향 벡터 계산
        dx = other_x - cap_x
        dy = other_y - cap_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            # 정규화된 방향 벡터
            nx = dx / length
            ny = dy / length
            
            # 수직 벡터
            px = -ny * width / 4
            py = nx * width / 4
            
            # 뾰족한 끝점
            tip_length = width / 3
            tip_x = cap_x - nx * tip_length
            tip_y = cap_y - ny * tip_length
            
            # 삼각형 점들
            points = [
                cap_x + px, cap_y + py,  # 한쪽 모서리
                cap_x - px, cap_y - py,  # 다른쪽 모서리
                tip_x, tip_y             # 뾰족한 끝
            ]
            
            draw.polygon(points, fill=color)
    
    def draw_rough_line(self, draw, coords, width, color, cap_style="둥글게"):
        """거친 효과 선 그리기"""
        x1, y1, x2, y2 = coords
        # 원래 굵기를 유지하면서 여러 개의 선으로 거친 효과 표현
        num_lines = max(3, width // 2)  # 최소 3개 선, 굵기에 따라 조정
        
        for i in range(num_lines):
            offset_x = random.randint(-1, 1)
            offset_y = random.randint(-1, 1)
            line_width = max(1, width // num_lines + random.randint(-1, 1))
            draw.line([x1+offset_x, y1+offset_y, x2+offset_x, y2+offset_y], 
                     fill=color, width=line_width)
        
        # 선끝 처리
        if cap_style == "둥글게":
            radius = width // 2
            for i in range(3):
                offset_x = random.randint(-1, 1)
                offset_y = random.randint(-1, 1)
                small_radius = max(1, radius // 2)
                draw.ellipse([x1-small_radius+offset_x, y1-small_radius+offset_y, 
                             x1+small_radius+offset_x, y1+small_radius+offset_y], fill=color)
                draw.ellipse([x2-small_radius+offset_x, y2-small_radius+offset_y, 
                             x2+small_radius+offset_x, y2+small_radius+offset_y], fill=color)
        elif cap_style == "뾰족하게":
            self.draw_pointed_cap(draw, x1, y1, x2, y2, width, color, True)
            self.draw_pointed_cap(draw, x2, y2, x1, y1, width, color, False)
    
    def lighten_color(self, hex_color, factor):
        """색상 밝게 하기"""
        # hex를 RGB로 변환
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # 밝게 조정
        new_rgb = tuple(min(255, int(c + (255-c)*factor)) for c in rgb)
        
        # 다시 hex로 변환
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)
    
    def darken_color(self, hex_color, factor):
        """색상 어둡게 하기"""
        # hex를 RGB로 변환
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # 어둡게 조정
        new_rgb = tuple(max(0, int(c * (1-factor))) for c in rgb)
        
        # 다시 hex로 변환
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)
    
    def apply_carving_effect(self, img):
        """조각 효과 적용"""
        if self.carving_var.get() == "양각":
            # 양각: 약간의 그림자 효과
            shadow_img = img.copy()
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=1))
            
            # 그림자를 약간 이동
            final_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
            final_img.paste(shadow_img, (1, 1), shadow_img)
            final_img.paste(img, (0, 0), img)
            return final_img
            
        elif self.carving_var.get() == "음각":
            # 음각: 내부 그림자 효과
            blur_img = img.filter(ImageFilter.GaussianBlur(radius=1))
            return blur_img
        
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
        elif border_type == "타원형":
            # 세로로 긴 타원
            draw.ellipse([margin+20, margin, size-margin-20, size-margin], 
                        outline=color, width=thickness)
        elif border_type == "긴타원형":
            # 더 긴 타원
            draw.ellipse([margin+40, margin, size-margin-40, size-margin], 
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