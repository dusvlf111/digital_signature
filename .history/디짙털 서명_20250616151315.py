import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk
import os

class DrawingCanvas:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=450, height=180, bg='white', 
                               relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(pady=5)
        
        # 그리기 관련 변수
        self.old_x = None
        self.old_y = None
        self.pen_width = 3
        self.pen_color = '#000080'
        
        # 그려진 선들을 저장할 리스트
        self.drawn_lines = []
        
        # 이벤트 바인딩
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonPress-1>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        
        # 컨트롤 버튼들
        control_frame = ttk.Frame(parent)
        control_frame.pack(pady=5)
        
        # 첫 번째 줄
        row1 = ttk.Frame(control_frame)
        row1.pack(pady=2)
        
        ttk.Button(row1, text="지우기", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="색상 변경", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        
        # 두 번째 줄
        row2 = ttk.Frame(control_frame)
        row2.pack(pady=2)
        
        ttk.Label(row2, text="펜 굵기:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.IntVar(value=3)
        width_scale = ttk.Scale(row2, from_=1, to=15, variable=self.width_var, 
                               orient=tk.HORIZONTAL, length=120)
        width_scale.pack(side=tk.LEFT, padx=5)
        width_scale.bind('<Motion>', self.update_pen_width)
        
        # 현재 설정 표시
        self.info_label = ttk.Label(row2, text=f"색상: {self.pen_color} | 굵기: {self.pen_width}")
        self.info_label.pack(side=tk.LEFT, padx=10)
        
    def paint(self, event):
        if self.old_x and self.old_y:
            line_id = self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                             width=self.pen_width, fill=self.pen_color,
                                             capstyle=tk.ROUND, smooth=tk.TRUE)
            # 선 정보 저장
            self.drawn_lines.append({
                'coords': [self.old_x, self.old_y, event.x, event.y],
                'width': self.pen_width,
                'color': self.pen_color
            })
        self.old_x = event.x
        self.old_y = event.y
        
    def reset(self, event):
        self.old_x = None
        self.old_y = None
        
    def clear_canvas(self):
        self.canvas.delete("all")
        self.drawn_lines = []
        messagebox.showinfo("완료", "캔버스가 지워졌습니다.")
        
    def choose_color(self):
        color = colorchooser.askcolor(title="펜 색상 선택")[1]
        if color:
            self.pen_color = color
            self.update_info_label()
            
    def update_pen_width(self, event):
        self.pen_width = self.width_var.get()
        self.update_info_label()
        
    def update_info_label(self):
        self.info_label.config(text=f"색상: {self.pen_color} | 굵기: {self.pen_width}")
        
    def get_image(self):
        """캔버스를 PIL 이미지로 변환 (정확한 선 재현)"""
        # 캔버스 크기 가져오기
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 새 이미지 생성 (투명 배경)
        img = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 저장된 모든 선들을 이미지에 그리기 (둥근 끝점 적용)
        for line in self.drawn_lines:
            coords = line['coords']
            width = line['width']
            color = line['color']
            
            # 선 그리기
            draw.line(coords, fill=color, width=width)
            
            # 둥근 끝점 그리기 (캔버스와 동일한 효과)
            x1, y1, x2, y2 = coords
            radius = width // 2
            
            # 시작점 원
            draw.ellipse([x1-radius, y1-radius, x1+radius, y1+radius], 
                        fill=color)
            # 끝점 원
            draw.ellipse([x2-radius, y2-radius, x2+radius, y2+radius], 
                        fill=color)
        
        return img

class HandwrittenSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("손글씨 서명 생성기")
        self.root.geometry("550x650")
        self.root.minsize(500, 600)
        
        self.current_image = None
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="손글씨 서명 생성기", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 안내 문구
        instruction_label = ttk.Label(main_frame, 
                                     text="아래 흰색 영역에 마우스로 서명을 그려주세요")
        instruction_label.pack(pady=(0, 5))
        
        # 그리기 캔버스
        canvas_frame = ttk.LabelFrame(main_frame, text="서명 그리기 영역", padding="5")
        canvas_frame.pack(fill=tk.X, pady=5)
        
        self.drawing_canvas = DrawingCanvas(canvas_frame)
        
        # 미리보기 섹션
        preview_frame = ttk.LabelFrame(main_frame, text="미리보기", padding="10")
        preview_frame.pack(fill=tk.X, pady=10)
        
        # 미리보기 영역을 캔버스 크기와 비슷하게 설정
        self.preview_canvas = tk.Canvas(preview_frame, width=450, height=180, 
                                       bg='white', relief=tk.SUNKEN, borderwidth=1)
        self.preview_canvas.pack()
        
        # 기본 안내 텍스트
        self.preview_canvas.create_text(225, 90, text="서명을 그린 후 '미리보기' 버튼을 눌러주세요", 
                                       fill='gray', font=('Arial', 10))
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        # 버튼들을 2줄로 배치
        button_row1 = ttk.Frame(button_frame)
        button_row1.pack(pady=2)
        
        ttk.Button(button_row1, text="미리보기", 
                  command=self.preview_signature, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_row1, text="이미지 저장", 
                  command=self.save_image, width=15).pack(side=tk.LEFT, padx=5)
        
        button_row2 = ttk.Frame(button_frame)
        button_row2.pack(pady=2)
        
        ttk.Button(button_row2, text="프로그램 종료", 
                  command=self.root.quit, width=15).pack()
        
    def preview_signature(self):
        """서명 미리보기 (캔버스에 직접 그리기)"""
        try:
            # 그려진 선이 있는지 확인
            if not self.drawing_canvas.drawn_lines:
                messagebox.showwarning("경고", "먼저 서명을 그려주세요.")
                return
            
            # 미리보기 캔버스 지우기
            self.preview_canvas.delete("all")
            
            # 그려진 선들을 미리보기 캔버스에 그대로 복사
            for line in self.drawing_canvas.drawn_lines:
                coords = line['coords']
                width = line['width']
                color = line['color']
                
                # 캔버스에 선 그리기 (원본과 동일한 스타일)
                self.preview_canvas.create_line(coords[0], coords[1], coords[2], coords[3],
                                              width=width, fill=color,
                                              capstyle=tk.ROUND, smooth=tk.TRUE)
            
            # PIL 이미지도 생성해서 저장용으로 준비
            self.current_image = self.drawing_canvas.get_image()
            
            messagebox.showinfo("완료", "미리보기가 생성되었습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"미리보기 생성 중 오류가 발생했습니다: {str(e)}")
    
    def save_image(self):
        """이미지 파일로 저장"""
        if self.current_image is None:
            messagebox.showwarning("경고", "먼저 '미리보기' 버튼을 눌러 서명을 생성해주세요.")
            return
        
        # 파일 저장 대화상자
        filename = filedialog.asksaveasfilename(
            title="서명 이미지 저장",
            defaultextension=".png",
            filetypes=[
                ("PNG 파일", "*.png"), 
                ("JPEG 파일", "*.jpg"), 
                ("모든 파일", "*.*")
            ]
        )
        
        if filename:
            try:
                # 투명 배경을 흰색으로 변경하여 저장 (JPG 호환성)
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    # JPG는 투명도를 지원하지 않으므로 흰색 배경 추가
                    background = Image.new('RGB', self.current_image.size, (255, 255, 255))
                    background.paste(self.current_image, mask=self.current_image.split()[-1])
                    background.save(filename, quality=95)
                else:
                    # PNG는 투명 배경 유지
                    self.current_image.save(filename)
                
                messagebox.showinfo("저장 완료", f"서명이 저장되었습니다:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("저장 실패", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")

def main():
    root = tk.Tk()
    app = HandwrittenSignatureApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()