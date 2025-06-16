import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import os
try:
    from scipy import ndimage
except ImportError:
    # scipy가 없으면 기본 기능만 사용
    ndimage = None

class BackgroundRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("누끼따기 전자서명/도장 생성기")
        self.root.geometry("900x800")
        self.root.minsize(800, 700)
        
        # 변수들
        self.original_image = None
        self.processed_image = None
        self.current_display_image = None
        
        # 설정값들
        self.threshold_var = tk.IntVar(value=200)
        self.blur_var = tk.IntVar(value=1)
        self.contrast_var = tk.DoubleVar(value=1.5)
        self.edge_smooth_var = tk.IntVar(value=2)
        self.shadow_removal_var = tk.BooleanVar(value=True)
        self.line_only_var = tk.BooleanVar(value=True)
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.shadow_threshold_var = tk.IntVar(value=150)
        
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
        
        ttk.Button(upload_frame, text="사용법 보기", 
                  command=self.show_usage_guide).pack(side=tk.LEFT, padx=10)
        
        self.file_label = ttk.Label(upload_frame, text="파일이 선택되지 않았습니다")
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 이미지 미리보기 섹션
        preview_frame = ttk.LabelFrame(main_frame, text="2. 이미지 미리보기 및 편집", padding="10")
        preview_frame.pack(fill=tk.X, pady=5)  # expand=True 제거
        
        # 이미지 표시 영역 (고정 크기)
        self.image_frame = ttk.Frame(preview_frame)
        self.image_frame.pack()
        
        self.image_label = ttk.Label(self.image_frame, text="이미지를 업로드해주세요", 
                                    width=50, height=15)  # 고정 크기 설정
        self.image_label.pack()
        
        # 설정 조절 섹션
        settings_frame = ttk.LabelFrame(main_frame, text="3. 배경 제거 설정", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 모드 선택
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="처리 모드:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Checkbutton(mode_frame, text="선만 추출 (그림자 제거)", 
                       variable=self.line_only_var, command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(mode_frame, text="그림자 제거 강화", 
                       variable=self.shadow_removal_var, command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        
        # 첫 번째 줄
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="배경 제거 강도:").pack(side=tk.LEFT)
        threshold_scale = ttk.Scale(row1, from_=150, to=250, variable=self.threshold_var,
                                   orient=tk.HORIZONTAL, length=120)
        threshold_scale.pack(side=tk.LEFT, padx=5)
        threshold_scale.bind('<Motion>', self.on_setting_change)
        
        ttk.Label(row1, text="그림자 제거 강도:").pack(side=tk.LEFT, padx=(20, 0))
        shadow_scale = ttk.Scale(row1, from_=100, to=200, variable=self.shadow_threshold_var,
                                orient=tk.HORIZONTAL, length=120)
        shadow_scale.pack(side=tk.LEFT, padx=5)
        shadow_scale.bind('<Motion>', self.on_setting_change)
        
        # 두 번째 줄
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="대비 강화:").pack(side=tk.LEFT)
        contrast_scale = ttk.Scale(row2, from_=1.0, to=4.0, variable=self.contrast_var,
                                  orient=tk.HORIZONTAL, length=120)
        contrast_scale.pack(side=tk.LEFT, padx=5)
        contrast_scale.bind('<Motion>', self.on_setting_change)
        
        ttk.Label(row2, text="밝기 조절:").pack(side=tk.LEFT, padx=(20, 0))
        brightness_scale = ttk.Scale(row2, from_=0.5, to=2.0, variable=self.brightness_var,
                                    orient=tk.HORIZONTAL, length=120)
        brightness_scale.pack(side=tk.LEFT, padx=5)
        brightness_scale.bind('<Motion>', self.on_setting_change)
        
        # 세 번째 줄
        row3 = ttk.Frame(settings_frame)
        row3.pack(fill=tk.X, pady=2)
        
        ttk.Label(row3, text="가장자리 부드럽게:").pack(side=tk.LEFT)
        blur_scale = ttk.Scale(row3, from_=0, to=5, variable=self.blur_var,
                              orient=tk.HORIZONTAL, length=120)
        blur_scale.pack(side=tk.LEFT, padx=5)
        blur_scale.bind('<Motion>', self.on_setting_change)
        
        ttk.Label(row3, text="가장자리 매끄럽게:").pack(side=tk.LEFT, padx=(20, 0))
        smooth_scale = ttk.Scale(row3, from_=0, to=5, variable=self.edge_smooth_var,
                                orient=tk.HORIZONTAL, length=120)
        smooth_scale.pack(side=tk.LEFT, padx=5)
        smooth_scale.bind('<Motion>', self.on_setting_change)
        
        # 처리 버튼들
        process_frame = ttk.Frame(settings_frame)
        process_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(process_frame, text="배경 제거 처리", 
                  command=self.process_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(process_frame, text="원본으로 되돌리기", 
                  command=self.reset_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(process_frame, text="선만 추출 최적화", 
                  command=self.auto_optimize_lines).pack(side=tk.LEFT, padx=5)
        ttk.Button(process_frame, text="일반 자동 최적화", 
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
            
        # 표시용 크기 조정 (더 작게)
        display_img = img.copy()
        display_img.thumbnail((350, 250), Image.Resampling.LANCZOS)  # 크기 줄임
        
        # tkinter용 변환
        photo = ImageTk.PhotoImage(display_img)
        
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo
        
        self.current_display_image = display_img
    
    def remove_white_background(self, img):
        """하얀 배경 제거 (그림자 제거 기능 포함)"""
        # 밝기 조절
        if self.brightness_var.get() != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(self.brightness_var.get())
        
        # 대비 강화
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(self.contrast_var.get())
        
        # PIL 이미지를 numpy 배열로 변환
        img_array = np.array(img)
        
        if self.line_only_var.get():
            # 선만 추출 모드
            return self.extract_lines_only(img_array)
        else:
            # 일반 배경 제거 모드
            return self.standard_background_removal(img_array)
    
    def extract_lines_only(self, img_array):
        """선만 추출하는 고급 처리"""
        height, width, channels = img_array.shape
        rgba_array = np.zeros((height, width, 4), dtype=np.uint8)
        
        # 그레이스케일 변환
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        
        # 그림자 제거를 위한 적응적 임계값 처리
        if self.shadow_removal_var.get() and ndimage is not None:
            # 지역별 평균 밝기 계산 (그림자 영역 감지)
            local_mean = ndimage.uniform_filter(gray.astype(np.float32), size=20)
            
            # 적응적 임계값 계산
            adaptive_threshold = local_mean - 30  # 지역 평균보다 30 낮으면 선으로 판단
            line_mask = gray < adaptive_threshold
            
            # 너무 밝은 부분은 제외 (그림자가 아닌 진짜 배경)
            bright_mask = gray > self.shadow_threshold_var.get()
            line_mask = line_mask & ~bright_mask
            
            # 노이즈 제거
            line_mask = ndimage.binary_opening(line_mask, structure=np.ones((2,2)))
            line_mask = ndimage.binary_closing(line_mask, structure=np.ones((3,3)))
        else:
            # scipy가 없거나 그림자 제거가 비활성화된 경우 단순 처리
            threshold = 255 - self.threshold_var.get()
            line_mask = gray < threshold
            
            # 기본 노이즈 제거 (scipy 없이)
            # 간단한 erosion/dilation 효과
            kernel = np.ones((3, 3), np.uint8)
            line_mask_expanded = np.zeros_like(line_mask)
            for i in range(1, height-1):
                for j in range(1, width-1):
                    if np.sum(line_mask[i-1:i+2, j-1:j+2]) >= 5:
                        line_mask_expanded[i, j] = True
            line_mask = line_mask_expanded
        
        # 결과 이미지 생성
        rgba_array[:, :, :3] = img_array  # 원본 색상 유지
        rgba_array[:, :, 3] = line_mask.astype(np.uint8) * 255  # 선 부분만 불투명
        
        # 배경을 완전히 투명하게
        rgba_array[~line_mask, 3] = 0
        
        # PIL 이미지로 변환
        result_img = Image.fromarray(rgba_array, 'RGBA')
        
        # 후처리
        return self.post_process_image(result_img)RGBA')
        
        # 후처리
        return self.post_process_image(result_img)
    
    def standard_background_removal(self, img_array):
        """기존 방식의 배경 제거"""
        height, width, channels = img_array.shape
        rgba_array = np.zeros((height, width, 4), dtype=np.uint8)
        rgba_array[:, :, :3] = img_array
        rgba_array[:, :, 3] = 255
        
        # 하얀색 픽셀 찾기
        threshold = self.threshold_var.get()
        white_mask = (img_array[:, :, 0] >= threshold) & \
                     (img_array[:, :, 1] >= threshold) & \
                     (img_array[:, :, 2] >= threshold)
        
        # 그림자 제거 추가 처리
        if self.shadow_removal_var.get():
            # 회색 계열 (그림자) 제거
            shadow_threshold = self.shadow_threshold_var.get()
            gray_diff = np.abs(img_array[:, :, 0].astype(int) - img_array[:, :, 1]) + \
                       np.abs(img_array[:, :, 1].astype(int) - img_array[:, :, 2]) + \
                       np.abs(img_array[:, :, 0].astype(int) - img_array[:, :, 2])
            
            shadow_mask = (gray_diff < 30) & \
                         (img_array[:, :, 0] > shadow_threshold) & \
                         (img_array[:, :, 1] > shadow_threshold) & \
                         (img_array[:, :, 2] > shadow_threshold)
            
            white_mask = white_mask | shadow_mask
        
        rgba_array[white_mask, 3] = 0
        
        result_img = Image.fromarray(rgba_array, 'RGBA')
        return self.post_process_image(result_img)
    
    def post_process_image(self, result_img):
        """이미지 후처리"""
        # 가장자리 부드럽게 하기
        if self.blur_var.get() > 0:
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
    
    def auto_optimize_lines(self):
        """선만 추출을 위한 자동 최적화"""
        if self.original_image is None:
            messagebox.showwarning("경고", "먼저 이미지를 업로드해주세요.")
            return
        
        # 선 추출 모드 활성화
        self.line_only_var.set(True)
        self.shadow_removal_var.set(True)
        
        # 이미지 분석
        img_array = np.array(self.original_image)
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        avg_brightness = np.mean(gray)
        contrast_level = np.std(gray)
        
        # 선 추출에 최적화된 설정
        if contrast_level < 30:  # 대비가 낮은 경우
            self.contrast_var.set(3.0)
            self.brightness_var.set(1.2)
            self.shadow_threshold_var.set(180)
        elif contrast_level < 60:  # 보통 대비
            self.contrast_var.set(2.5)
            self.brightness_var.set(1.1)
            self.shadow_threshold_var.set(160)
        else:  # 대비가 높은 경우
            self.contrast_var.set(2.0)
            self.brightness_var.set(1.0)
            self.shadow_threshold_var.set(140)
        
        # 밝기에 따른 임계값 조정
        if avg_brightness > 200:
            self.threshold_var.set(240)
        elif avg_brightness > 150:
            self.threshold_var.set(220)
        else:
            self.threshold_var.set(200)
        
        # 부드럽게 처리
        self.blur_var.set(1)
        self.edge_smooth_var.set(1)
        
        # 처리 실행
        self.process_image()
        messagebox.showinfo("완료", "선 추출 최적화가 완료되었습니다!")
    
    def auto_optimize(self):
        """일반 자동 최적화"""
        if self.original_image is None:
            messagebox.showwarning("경고", "먼저 이미지를 업로드해주세요.")
            return
        
        # 일반 모드
        self.line_only_var.set(False)
        self.shadow_removal_var.set(True)
        
        # 이미지 분석해서 최적값 설정
        img_array = np.array(self.original_image)
        avg_brightness = np.mean(img_array)
        
        if avg_brightness > 200:  # 매우 밝은 이미지
            self.threshold_var.set(220)
            self.contrast_var.set(2.0)
            self.shadow_threshold_var.set(170)
        elif avg_brightness > 150:  # 보통 밝기
            self.threshold_var.set(200)
            self.contrast_var.set(1.5)
            self.shadow_threshold_var.set(150)
        else:  # 어두운 이미지
            self.threshold_var.set(180)
            self.contrast_var.set(2.5)
            self.shadow_threshold_var.set(130)
        
        # 기본값
        self.brightness_var.set(1.0)
        self.blur_var.set(1)
        self.edge_smooth_var.set(2)
        
        # 처리 실행
        self.process_image()
        messagebox.showinfo("완료", "일반 자동 최적화가 완료되었습니다!")
    
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
    
    def show_usage_guide(self):
        """사용법 안내창 표시"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("사용법 안내")
        guide_window.geometry("600x500")
        guide_window.resizable(False, False)
        
        # 창을 부모 창 중앙에 배치
        guide_window.transient(self.root)
        guide_window.grab_set()
        
        # 스크롤 가능한 텍스트 위젯
        main_frame = ttk.Frame(guide_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="누끼따기 전자서명/도장 생성기 사용법", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 텍스트 영역
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                             font=('Arial', 10), padx=10, pady=10)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_widget.yview)
        
        # 사용법 내용
        usage_text = """
📸 사진 촬영 팁
• 하얀 A4 용지에 서명이나 도장을 찍으세요
• 밝은 곳에서 그림자 없이 촬영하세요
• 서명/도장이 선명하게 보이도록 촬영하세요
• 용지가 화면에 꽉 차도록 촬영하세요

🚀 기본 사용법
1. '이미지 파일 선택' 버튼으로 사진 업로드
2. 자동으로 첫 처리가 실행됩니다
3. 결과가 만족스러우면 바로 저장하세요

⚙️ 그림자가 있는 경우
1. "선만 추출 (그림자 제거)" ✅ 체크
2. "그림자 제거 강화" ✅ 체크
3. "선만 추출 최적화" 버튼 클릭
4. 결과 확인 후 세부 조정

🔧 수동 조정 방법
• 배경 제거 강도: 150~250 (높을수록 더 많이 제거)
• 그림자 제거 강도: 100~200 (낮을수록 더 많이 제거)
• 대비 강화: 1.0~4.0 (높을수록 선명하게)
• 밝기 조절: 0.5~2.0 (1.0이 원본)
• 가장자리 부드럽게: 0~5 (높을수록 부드럽게)
• 가장자리 매끄럽게: 0~5 (높을수록 매끄럽게)

💡 최적화 버튼 활용
• "선만 추출 최적화": 서명/도장 선만 깔끔하게
• "일반 자동 최적화": 기존 방식 배경 제거

💾 저장 옵션
• "투명 배경 PNG로 저장": 진짜 전자 서명/도장용
• "흰색 배경 JPG로 저장": 일반 문서용

⚠️ 문제 해결
• 선이 잘려나가면: 배경 제거 강도를 낮추세요
• 배경이 남아있으면: 그림자 제거 강도를 낮추세요
• 선이 흐리면: 대비 강화를 높이세요
• 가장자리가 거칠면: 부드럽게/매끄럽게 값을 높이세요

📋 권장 설정 (그림자 있는 경우)
• 선만 추출: ✅
• 그림자 제거 강화: ✅
• 배경 제거 강도: 220
• 그림자 제거 강도: 150
• 대비 강화: 2.5
• 밝기 조절: 1.1
• 가장자리 부드럽게: 1
• 가장자리 매끄럽게: 1

🎯 최상의 결과를 위한 팁
• 조명이 균일한 곳에서 촬영
• 서명/도장과 배경의 대비가 클수록 좋음
• 용지에 주름이나 얼룩이 없어야 함
• 스마트폰을 수직으로 들고 촬영
        """
        
        text_widget.insert(tk.END, usage_text)
        text_widget.config(state=tk.DISABLED)  # 읽기 전용
        
        # 닫기 버튼
        close_btn = ttk.Button(main_frame, text="닫기", command=guide_window.destroy)
        close_btn.pack(pady=15)
    
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