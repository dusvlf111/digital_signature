import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk
import os

class DrawableStampMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("직접 그리는 도장 생성기")
        self.root.geometry("1200x800")
        self.root.minsize(1100, 750)
        
        # 도장 설정 변수들
        self.stamp_size_var = tk.IntVar(value=300)
        self.border_type_var = tk.StringVar(value="사각형")
        self.border_thickness_var = tk.IntVar(value=3)
        self.grid_type_var = tk.StringVar(value="2x2")
        self.grid_thickness_var = tk.IntVar(value=1)
        self.show_grid_var = tk.BooleanVar(value=True)
        self.stamp_color_var = tk.StringVar(value="#CC0000")
        
        # 그리기 관련 변수
        self.pen_width = 3
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
        settings_frame = ttk.LabelFrame(content_frame, text="도장 설정", padding="10", width=280)
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
        border_scale = ttk.Scale(border_frame, from_=1, to=10, variable=self.border_thickness_var,
                                orient=tk.HORIZONTAL, command=self.update_guides)
        border_scale.pack(fill=tk.X, pady=2)
        ttk.Label(border_frame, textvariable=self.border_thickness_var).pack()
        
        # 가이드 그리드
        grid_frame = ttk.LabelFrame(parent, text="가이드 그리드", padding="5")
        grid_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(grid_frame, text="가이드 표시", 
                       variable=self.show_grid_var, command=self.update_guides).pack(anchor=tk.W)
        
        ttk.Label(grid_frame, text="칸 나누기:").pack(anchor=tk.W)
        grid_combo = ttk.Combobox(grid_frame, textvariable=self.grid_type_var,
                                 values=["없음", "1x2", "2x1", "2x2", "1x3", "3x1", "2x3", "3x2", "3x3"], 
                                 state="readonly", width=20)
        grid_combo.pack(fill=tk.X, pady=2)
        grid_combo.bind('<<ComboboxSelected>>', self.update_guides)
        
        ttk.Label(grid_frame, text="그리드 두께:").pack(anchor=tk.W)
        grid_scale = ttk.Scale(grid_frame, from_=1, to=5, variable=self.grid_thickness_var,
                              orient=tk.HORIZONTAL, command=self.update_guides)
        grid_scale.pack(fill=tk.X, pady=2)
        ttk.Label(grid_frame, textvariable=self.grid_thickness_var).pack()
        
        # 그리기 도구
        pen_frame = ttk.LabelFrame(parent, text="그리기 도구", padding="5")
        pen_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(pen_frame, text="펜 색상", command=self.choose_pen_color).pack(fill=tk.X, pady=2)
        self.pen_color_display = tk.Label(pen_frame, bg=self.pen_color, 
                                         height=1, relief=tk.SUNKEN)
        self.pen_color_display.pack(fill=tk.X, pady=2)
        
        ttk.Label(pen_frame, text="펜 굵기:").pack(anchor=tk.W)
        self.pen_width_var = tk.IntVar(value=3)
        pen_scale = ttk.Scale(pen_frame, from_=1, to=20, variable=self.pen_width_var,
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
        
        if not self.show_grid_var.get():
            return
            
        size = self.stamp_size_var.get()
        border_type = self.border_type_var.get()
        border_thickness = self.border_thickness_var.get()
        grid_type = self.grid_type_var.get()
        grid_thickness = self.grid_thickness_var.get()
        
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
                # 둥근 사각형 근사 (직선들로)
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
        if grid_type != "없음":
            rows, cols = map(int, grid_type.split('x'))
            margin = 25
            grid_width = size - 2 * margin
            grid_height = size - 2 * margin
            
            cell_width = grid_width / cols
            cell_height = grid_height / rows
            
            # 세로 선
            for i in range(1, cols):
                x = margin + i * cell_width
                self.drawing_canvas.create_line(x, margin, x, size-margin, 
                                              fill=guide_color, width=grid_thickness, tags="guide")
            
            # 가로 선
            for i in range(1, rows):
                y = margin + i * cell_height
                self.drawing_canvas.create_line(margin, y, size-margin, y, 
                                              fill=guide_color, width=grid_thickness, tags="guide")
    
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
        
        # 이미지 생성
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 외부 테두리 그리기
        self.draw_border(draw, size, final_color)
        
        # 그려진 선들을 최종 색상으로 그리기
        for line in self.drawn_lines:
            coords = line['coords']
            width = line['width']
            
            # 최종 도장 색상으로 변경
            draw.line(coords, fill=final_color, width=width)
            
            # 둥근 끝점 추가
            x1, y1, x2, y2 = coords
            radius = width // 2
            draw.ellipse([x1-radius, y1-radius, x1+radius, y1+radius], fill=final_color)
            draw.ellipse([x2-radius, y2-radius, x2+radius, y2+radius], fill=final_color)
        
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