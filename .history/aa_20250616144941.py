import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import os

class BackgroundRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("누끼따기 전자서명/도장 생성기")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # 변수들
        self.original_image = None
        self.processed_image = None
        self.current_display_image = None
        
        # 설정값들
        self.threshold_var = tk.IntVar(value=200)
        self.blur_var = tk.IntVar(value=1)
        self.contrast_var = tk.DoubleVar(value=1.5)
        self.edge_smooth_var = tk.IntVar(value=2)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="누끼따기 전자서명/도장 생성기", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 안내문
        info_label = ttk.Label(main_frame, 
                              text="하얀 배경에 서명이나 도장이 있는 사진을 업로드하면 배경을 제거해서 투명한 전자 서명/도장을 만들어줍니다")
        info_label.pack(pady=(0, 15))
        
        # 파일 업로드 섹션
        upload_frame = ttk.LabelFrame(main_frame, text="1. 이미지 업로드", padding="10")
        upload_frame.pack(fill=tk.X, pady=5)
        
        upload_btn = ttk.Button(upload_frame, text="이미지 파일 선택", 
                               command=self.load_image)
        upload_btn.pack(side=tk.LEFT)
        
        self.file_label = ttk.Label(upload_frame, text="파일이 선택되지 않았습니다")
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 이미지 미리보기 섹션
        preview_frame = ttk.LabelFrame(main_frame, text="2. 이미지 미리보기 및 편집", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 이미지 표시 영역
        self.image_frame = ttk.Frame(preview_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_label = ttk.Label(self.image_frame, text="이미지를 업로드해주세요")
        self.image_label.pack(expand=True)
        
        # 설정 조절 섹션
        settings_frame = ttk.LabelFrame(main_frame, text="3. 배경 제거 설정", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 첫 번째 줄
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="배경 제거 강도:").pack(side=tk.LEFT)
        threshold_scale = ttk.Scale(row1, from_=150, to=250, variable=self.threshold_var,
                                   orient=tk.HORIZONTAL, length=150)
        threshold_scale.pack(side=tk.LEFT, padx=5)
        threshold_scale.bind('<Motion>', self.on_setting_change)
        
        ttk.Label(row1, text="가장자리 부드럽게:").pack(side=tk.LEFT, padx=(20, 0))
        blur_scale = ttk.Scale(row1, from_=0, to=5, variable=self.blur_var,
                              orient=tk.HORIZONTAL, length=100)
        blur_scale.pack(side=tk.LEFT, padx=5)
        blur_scale.bind('<Motion>', self.on_setting_change)
        
        # 두 번째 줄
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="대비 강화:").pack(side=tk.LEFT)
        contrast_scale = ttk.Scale(row2, from_=1.0, to=3.0, variable=self.contrast_var,
                                  orient=tk.HORIZONTAL, length=150)
        contrast_scale.pack(side=tk.LEFT, padx=5)
        contrast_scale.bind('<Motion>', self.on_setting_change)
        
        ttk.Label(row2, text="가장자리 매끄럽게:").pack(side=tk.LEFT, padx=(20, 0))
        smooth_scale = ttk.Scale(row2, from_=0, to=5, variable=self.edge_smooth_var,
                                orient=tk.HORIZONTAL, length=100)
        smooth_scale.pack(side=tk.LEFT, padx=5)
        smooth_scale.bind('<Motion>', self.on_setting_change)
        
        # 처리 버튼들
        process_frame = ttk.Frame(settings_frame)
        process_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(process_frame, text="배경 제거 처리", 
                  command=self.process_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(process_frame, text="원본으로 되돌리기", 
                  command=self.reset_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(process_frame, text="자동 최적화", 
                  command=self.auto_optimize).pack(side=tk.LEFT, padx=5)
        
        # 저장 섹션
        save_frame = ttk.LabelFrame(main_frame, text="4. 저장", padding="10")
        save_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(save_frame, text="투명 배경 PNG로 저장", 
                  command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_frame, text="흰색 배경 JPG로 저장", 
                  command=self.save_image_white_bg).pack(side=tk.LEFT, padx=5)
        
    def load_image(self):
        """이미지 파일 로드"""
        file_path = filedialog.askopenfilename(
            title="서명/도장 이미지 선택",
            filetypes=[
                ("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("모든 파일", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 이미지 로드
                self.original_image = Image.open(file_path)
                
                # RGB로 변환 (RGBA나 다른 모드일 수 있음)
                if self.original_image.mode != 'RGB':
                    self.original_image = self.original_image.convert('RGB')
                
                # 파일명 표시
                filename = os.path.basename(file_path)
                self.file_label.config(text=f"선택된 파일: {filename}")
                
                # 이미지 표시
                self.display_image(self.original_image)
                
                # 자동으로 첫 처리 실행
                self.process_image()
                
                messagebox.showinfo("완료", "이미지가 성공적으로 로드되었습니다!")
                
            except Exception as e:
                messagebox.showerror("오류", f"이미지 로드 중 오류가 발생했습니다:\n{str(e)}")
    
    def display_image(self, img):
        """이미지를 화면에 표시"""
        if img is None:
            return
            
        # 표시용 크기 조정
        display_img = img.copy()
        display_img.thumbnail((400, 300), Image.Resampling.LANCZOS)
        
        # tkinter용 변환
        photo = ImageTk.PhotoImage(display_img)
        
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo
        
        self.current_display_image = display_img
    
    def remove_white_background(self, img):
        """하얀 배경 제거"""
        # PIL 이미지를 numpy 배열로 변환
        img_array = np.array(img)
        
        # 대비 강화
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(self.contrast_var.get())
        img_array = np.array(img)
        
        # RGB를 RGBA로 변환
        height, width, channels = img_array.shape
        rgba_array = np.zeros((height, width, 4), dtype=np.uint8)
        rgba_array[:, :, :3] = img_array
        rgba_array[:, :, 3] = 255  # 알파 채널 초기화
        
        # 하얀색 픽셀 찾기 (임계값 사용)
        threshold = self.threshold_var.get()
        white_mask = (img_array[:, :, 0] >= threshold) & \
                     (img_array[:, :, 1] >= threshold) & \
                     (img_array[:, :, 2] >= threshold)
        
        # 하얀색 픽셀을 투명하게 만들기
        rgba_array[white_mask, 3] = 0
        
        # numpy 배열을 PIL 이미지로 변환
        result_img = Image.fromarray(rgba_array, 'RGBA')
        
        # 가장자리 부드럽게 하기
        if self.blur_var.get() > 0:
            # 알파 채널만 블러 처리
            alpha = result_img.split()[3]
            alpha_blurred = alpha.filter(ImageFilter.GaussianBlur(self.blur_var.get()))
            result_img.putalpha(alpha_blurred)
        
        # 가장자리 매끄럽게 하기
        if self.edge_smooth_var.get() > 0:
            alpha = result_img.split()[3]
            for _ in range(self.edge_smooth_var.get()):
                alpha = alpha.filter(ImageFilter.SMOOTH)
            result_img.putalpha(alpha)
        
        return result_img
    
    def process_image(self):
        """배경 제거 처리"""
        if self.original_image is None:
            messagebox.showwarning("경고", "먼저 이미지를 업로드해주세요.")
            return
        
        try:
            # 배경 제거
            self.processed_image = self.remove_white_background(self.original_image)
            
            # 결과 표시
            self.display_image(self.processed_image)
            
        except Exception as e:
            messagebox.showerror("오류", f"이미지 처리 중 오류가 발생했습니다:\n{str(e)}")
    
    def reset_image(self):
        """원본 이미지로 되돌리기"""
        if self.original_image is None:
            messagebox.showwarning("경고", "원본 이미지가 없습니다.")
            return
        
        self.display_image(self.original_image)
        self.processed_image = None
    
    def auto_optimize(self):
        """자동 최적화"""
        if self.original_image is None:
            messagebox.showwarning("경고", "먼저 이미지를 업로드해주세요.")
            return
        
        # 이미지 분석해서 최적값 설정
        img_array = np.array(self.original_image)
        
        # 밝기 평균 계산
        avg_brightness = np.mean(img_array)
        
        if avg_brightness > 200:  # 매우 밝은 이미지
            self.threshold_var.set(220)
            self.contrast_var.set(2.0)
        elif avg_brightness > 150:  # 보통 밝기
            self.threshold_var.set(200)
            self.contrast_var.set(1.5)
        else:  # 어두운 이미지
            self.threshold_var.set(180)
            self.contrast_var.set(2.5)
        
        # 기본 부드럽게 설정
        self.blur_var.set(1)
        self.edge_smooth_var.set(2)
        
        # 자동 처리 실행
        self.process_image()
        
        messagebox.showinfo("완료", "자동 최적화가 완료되었습니다!")
    
    def on_setting_change(self, event):
        """설정값 변경 시 실시간 처리"""
        if self.original_image is not None:
            # 약간의 지연을 두고 처리 (너무 빠른 처리 방지)
            self.root.after(100, self.process_image)
    
    def save_image(self):
        """투명 배경 PNG로 저장"""
        if self.processed_image is None:
            messagebox.showwarning("경고", "먼저 배경 제거 처리를 해주세요.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="투명 배경 이미지 저장",
            defaultextension=".png",
            filetypes=[("PNG 파일", "*.png")]
        )
        
        if file_path:
            try:
                self.processed_image.save(file_path, "PNG")
                messagebox.showinfo("저장 완료", f"투명 배경 이미지가 저장되었습니다:\n{file_path}")
            except Exception as e:
                messagebox.showerror("저장 실패", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def save_image_white_bg(self):
        """흰색 배경 JPG로 저장"""
        if self.processed_image is None:
            messagebox.showwarning("경고", "먼저 배경 제거 처리를 해주세요.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="흰색 배경 이미지 저장",
            defaultextension=".jpg",
            filetypes=[("JPEG 파일", "*.jpg"), ("PNG 파일", "*.png")]
        )
        
        if file_path:
            try:
                # 흰색 배경 추가
                white_bg = Image.new('RGB', self.processed_image.size, (255, 255, 255))
                white_bg.paste(self.processed_image, mask=self.processed_image.split()[3])
                
                if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    white_bg.save(file_path, "JPEG", quality=95)
                else:
                    white_bg.save(file_path, "PNG")
                
                messagebox.showinfo("저장 완료", f"흰색 배경 이미지가 저장되었습니다:\n{file_path}")
            except Exception as e:
                messagebox.showerror("저장 실패", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")

def main():
    root = tk.Tk()
    app = BackgroundRemover(root)
    root.mainloop()

if __name__ == "__main__":
    main()