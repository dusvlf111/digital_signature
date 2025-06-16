import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font
from PIL import Image, ImageDraw, ImageFont, ImageTk
import math
import os

class CustomStampMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("사용자 정의 도장 생성기")
        self.root.geometry("1000x800")
        self.root.minsize(950, 750)
        
        # 도장 설정 변수들
        self.stamp_size_var = tk.IntVar(value=200)
        self.border_type_var = tk.StringVar(value="사각형")
        self.border_thickness_var = tk.IntVar(value=3)
        self.grid_type_var = tk.StringVar(value="2x2")
        self.stamp_color_var = tk.StringVar(value="#CC0000")
        
        # 그리드 셀 텍스트 저장
        self.cell_texts = {}
        self.cell_entries = {}
        self.font_size_var = tk.IntVar(value=20)
        
        # 사용 가능한 폰트 목록
        self.available_fonts = self.get_available_fonts()
        self.selected_font_var = tk.StringVar(value=self.available_fonts[0] if self.available_fonts else "Arial")
        
        self.current_image = None
        self.setup_ui()
        
    def get_available_fonts(self):
        """시스템 폰트 목록 가져오기"""
        try:
            tk_fonts = list(font.families())
            common_fonts = ["맑은 고딕", "굴림", "돋움", "바탕", "Arial", "Times New Roman"]
            
            available = []
            for f in common_fonts + tk_fonts:
                if f not in available:
                    available.append(f)
            
            return available[:20]  # 20개로 제한
        except:
            return ["Arial", "맑은 고딕", "굴림"]
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="사용자 정의 도장 생성기", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 3분할 레이아웃
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 기본 설정
        settings_frame = ttk.LabelFrame(content_frame, text="기본 설정", padding="10", width=250)
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        settings_frame.pack_propagate(False)
        
        # 가운데: 텍스트 입력
        text_frame = ttk.LabelFrame(content_frame, text="텍스트 입력", padding="10", width=300)
        text_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        text_frame.pack_propagate(False)
        
        # 오른쪽: 미리보기
        preview_frame = ttk.LabelFrame(content_frame, text="미리보기", padding="10")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.setup_settings_panel(settings_frame)
        self.setup_text_panel(text_frame)
        self.setup_preview_panel(preview_frame)
        
    def setup_settings_panel(self, parent):
        # 도장 크기
        size_frame = ttk.LabelFrame(parent, text="도장 크기", padding="5")
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="크기:").pack(anchor=tk.W)
        size_scale = ttk.Scale(size_frame, from_=150, to=400, variable=self.stamp_size_var,
                              orient=tk.HORIZONTAL, command=self.on_setting_change)
        size_scale.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, textvariable=self.stamp_size_var).pack()
        
        # 외부 테두리
        border_frame = ttk.LabelFrame(parent, text="외부 테두리", padding="5")
        border_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(border_frame, text="모양:").pack(anchor=tk.W)
        border_combo = ttk.Combobox(border_frame, textvariable=self.border_type_var,
                                   values=["사각형", "원형", "둥근사각형", "없음"], 
                                   state="readonly", width=15)
        border_combo.pack(fill=tk.X, pady=2)
        border_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        
        ttk.Label(border_frame, text="두께:").pack(anchor=tk.W)
        border_scale = ttk.Scale(border_frame, from_=1, to=10, variable=self.border_thickness_var,
                                orient=tk.HORIZONTAL, command=self.on_setting_change)
        border_scale.pack(fill=tk.X, pady=2)
        ttk.Label(border_frame, textvariable=self.border_thickness_var).pack()
        
        # 그리드 설정
        grid_frame = ttk.LabelFrame(parent, text="칸 나누기", padding="5")
        grid_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(grid_frame, text="배치:").pack(anchor=tk.W)
        grid_combo = ttk.Combobox(grid_frame, textvariable=self.grid_type_var,
                                 values=["1x1", "1x2", "2x1", "2x2", "1x3", "3x1", "2x3", "3x2"], 
                                 state="readonly", width=15)
        grid_combo.pack(fill=tk.X, pady=2)
        grid_combo.bind('<<ComboboxSelected>>', self.update_text_grid)
        
        # 폰트 설정
        font_frame = ttk.LabelFrame(parent, text="폰트 설정", padding="5")
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="폰트:").pack(anchor=tk.W)
        font_combo = ttk.Combobox(font_frame, textvariable=self.selected_font_var,
                                 values=self.available_fonts, state="readonly", width=15)
        font_combo.pack(fill=tk.X, pady=2)
        font_combo.bind('<<ComboboxSelected>>', self.on_setting_change)
        
        ttk.Label(font_frame, text="크기:").pack(anchor=tk.W)
        font_scale = ttk.Scale(font_frame, from_=10, to=50, variable=self.font_size_var,
                              orient=tk.HORIZONTAL, command=self.on_setting_change)
        font_scale.pack(fill=tk.X, pady=2)
        ttk.Label(font_frame, textvariable=self.font_size_var).pack()
        
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
        
    def setup_text_panel(self, parent):
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 초기 그리드 생성
        self.update_text_grid()
        
    def setup_preview_panel(self, parent):
        # 미리보기 캔버스
        self.preview_canvas = tk.Canvas(parent, width=450, height=450, 
                                       bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.preview_canvas.pack(expand=True, pady=20)
        
        # 안내 텍스트
        self.preview_canvas.create_text(225, 225, text="텍스트를 입력하고\n'미리보기 생성' 버튼을 눌러주세요", 
                                       fill='gray', font=('Arial', 12), justify=tk.CENTER)
        
    def update_text_grid(self, event=None):
        """그리드 타입에 따라 텍스트 입력 필드 업데이트"""
        # 기존 위젯들 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.cell_entries = {}
        
        grid_type = self.grid_type_var.get()
        rows, cols = map(int, grid_type.split('x'))
        
        # 안내 라벨
        info_label = ttk.Label(self.scrollable_frame, 
                              text=f"{grid_type} 배치 - 각 칸에 들어갈 텍스트를 입력하세요",
                              font=('Arial', 10, 'bold'))
        info_label.pack(pady=10)
        
        # 그리드 생성
        grid_frame = ttk.Frame(self.scrollable_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        for row in range(rows):
            for col in range(cols):
                cell_key = f"{row}_{col}"
                
                # 셀 프레임
                cell_frame = ttk.LabelFrame(grid_frame, text=f"칸 ({row+1}, {col+1})", padding="5")
                cell_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                
                # 텍스트 입력
                entry = tk.Text(cell_frame, width=15, height=3, wrap=tk.WORD)
                entry.pack(fill=tk.BOTH, expand=True)
                
                # 기존 텍스트가 있으면 복원
                if cell_key in self.cell_texts:
                    entry.insert('1.0', self.cell_texts[cell_key])
                
                # 엔트리 저장
                self.cell_entries[cell_key] = entry
                
                # 텍스트 변경 이벤트 바인딩
                entry.bind('<KeyRelease>', self.on_text_change)
                
        # 그리드 컬럼 가중치 설정
        for col in range(cols):
            grid_frame.columnconfigure(col, weight=1)
            
        # 자동 미리보기 버튼
        auto_frame = ttk.Frame(self.scrollable_frame)
        auto_frame.pack(pady=10)
        
        ttk.Button(auto_frame, text="실시간 미리보기 켜기", 
                  command=self.toggle_auto_preview).pack()
        
        self.auto_preview = False
        
    def on_text_change(self, event=None):
        """텍스트 변경 시 저장"""
        for cell_key, entry in self.cell_entries.items():
            self.cell_texts[cell_key] = entry.get('1.0', 'end-1c')
            
        if hasattr(self, 'auto_preview') and self.auto_preview:
            self.root.after(500, self.generate_preview)
            
    def toggle_auto_preview(self):
        """실시간 미리보기 토글"""
        self.auto_preview = not self.auto_preview
        
    def on_setting_change(self, event=None):
        """설정 변경 시 자동 미리보기 (실시간 모드일 때만)"""
        if hasattr(self, 'auto_preview') and self.auto_preview:
            self.root.after(100, self.generate_preview)
            
    def choose_color(self):
        """색상 선택"""
        color = colorchooser.askcolor(title="도장 색상 선택")[1]
        if color:
            self.stamp_color_var.set(color)
            self.color_display.config(bg=color)
            self.on_setting_change()
            
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
            messagebox.showerror("오류", f"미리보기 생성 중 오류가 발생했습니다:\n{str(e)}")
            
    def create_stamp_image(self):
        """도장 이미지 생성"""
        size = self.stamp_size_var.get()
        
        # 이미지 생성
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        color = self.stamp_color_var.get()
        
        # 외부 테두리 그리기
        self.draw_border(draw, size, color)
        
        # 그리드와 텍스트 그리기
        self.draw_grid_and_text(draw, size, color)
        
        return img
        
    def draw_border(self, draw, size, color):
        """외부 테두리 그리기"""
        border_type = self.border_type_var.get()
        thickness = self.border_thickness_var.get()
        margin = 5
        
        if border_type == "없음":
            return
            
        if border_type == "사각형":
            draw.rectangle([margin, margin, size-margin, size-margin], 
                          outline=color, width=thickness)
        elif border_type == "원형":
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        outline=color, width=thickness)
        elif border_type == "둥근사각형":
            # 둥근 사각형 (여러 개의 호와 선으로 구현)
            corner_radius = 20
            draw.rounded_rectangle([margin, margin, size-margin, size-margin], 
                                  radius=corner_radius, outline=color, width=thickness)
            
    def draw_grid_and_text(self, draw, size, color):
        """그리드와 텍스트 그리기"""
        grid_type = self.grid_type_var.get()
        rows, cols = map(int, grid_type.split('x'))
        
        # 그리드 영역 계산 (테두리 여백 고려)
        margin = 20
        grid_width = size - 2 * margin
        grid_height = size - 2 * margin
        
        cell_width = grid_width / cols
        cell_height = grid_height / rows
        
        # 그리드 선 그리기 (2x2 이상일 때만)
        if rows > 1 or cols > 1:
            # 세로 선
            for i in range(1, cols):
                x = margin + i * cell_width
                draw.line([x, margin, x, size-margin], fill=color, width=1)
                
            # 가로 선
            for i in range(1, rows):
                y = margin + i * cell_height
                draw.line([margin, y, size-margin, y], fill=color, width=1)
        
        # 텍스트 그리기
        font_size = self.font_size_var.get()
        font_name = self.selected_font_var.get()
        
        # 폰트 로드
        try:
            if font_name in ["맑은 고딕", "Malgun Gothic"]:
                font = ImageFont.truetype("malgun.ttf", font_size)
            elif font_name == "굴림":
                font = ImageFont.truetype("gulim.ttc", font_size)
            elif font_name == "돋움":
                font = ImageFont.truetype("dotum.ttc", font_size)
            elif font_name == "바탕":
                font = ImageFont.truetype("batang.ttc", font_size)
            else:
                font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # 각 셀에 텍스트 그리기
        for row in range(rows):
            for col in range(cols):
                cell_key = f"{row}_{col}"
                text = self.cell_texts.get(cell_key, "")
                
                if text.strip():
                    # 셀 중심 계산
                    center_x = margin + col * cell_width + cell_width / 2
                    center_y = margin + row * cell_height + cell_height / 2
                    
                    # 여러 줄 텍스트 처리
                    lines = text.strip().split('\n')
                    total_height = len(lines) * font_size
                    start_y = center_y - total_height / 2
                    
                    for i, line in enumerate(lines):
                        if line.strip():
                            y = start_y + i * font_size
                            draw.text((center_x, y), line.strip(), 
                                    font=font, fill=color, anchor="mm")
            
    def display_on_canvas(self, img):
        """캔버스에 이미지 표시"""
        # 캔버스 크기에 맞게 조정
        display_img = img.copy()
        display_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # tkinter 포토 이미지로 변환
        photo = ImageTk.PhotoImage(display_img)
        
        # 캔버스 중앙에 표시
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            x = canvas_width // 2
            y = canvas_height // 2
            self.preview_canvas.create_image(x, y, image=photo)
            self.preview_canvas.image = photo
            
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
    app = CustomStampMaker(root)
    root.mainloop()

if __name__ == "__main__":
    main()