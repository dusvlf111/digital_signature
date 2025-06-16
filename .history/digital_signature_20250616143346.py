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
        
        # 그려진 선들을 저장할 리스트
        self.drawn_lines = []
        
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
        
    def choose_color(self):
        color = colorchooser.askcolor(title="펜 색상 선택")[1]
        if color:
            self.pen_color = color
            
    def update_pen_width(self, event):
        self.pen_width = self.width_var.get()
        
    def get_image(self):
        """캔버스를 PIL 이미지로 변환"""
        # 캔버스 크기 가져오기
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 새 이미지 생성 (투명 배경)
        img = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 저장된 모든 선들을 이미지에 그리기
        for line in self.drawn_lines:
            coords = line['coords']
            width = line['width']
            color = line['color']
            
            # PIL에서 선 그리기
            draw.line(coords, fill=color, width=width)
        
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
        self.selected_font = "Default"
        self.font_files = {}  # 폰트명: 파일경로 매핑
        
        # 사용 가능한 폰트 목록 가져오기 (시간이 걸릴 수 있음)
        print("시스템 폰트를 스캔하는 중...")
        self.available_fonts = self.get_available_fonts()
        print(f"폰트 스캔 완료: {len(self.available_fonts)}개 발견")
        
        self.setup_ui()
        
    def get_available_fonts(self):
        """시스템에서 사용 가능한 모든 폰트 목록을 가져옵니다."""
        available_fonts = ["Default"]  # 기본 폰트를 맨 위에
        font_files = {}  # 폰트명: 파일경로 매핑
        
        # 시스템별 폰트 디렉토리 정의
        font_directories = []
        
        if os.name == 'nt':  # Windows
            font_directories = [
                'C:/Windows/Fonts/',
                'C:/Windows/System32/Fonts/',
                os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/'),
                os.path.expanduser('~/AppData/Roaming/Microsoft/Windows/Fonts/')
            ]
        elif hasattr(os, 'uname') and os.uname().sysname == 'Darwin':  # macOS
            font_directories = [
                '/System/Library/Fonts/',
                '/Library/Fonts/',
                '/Network/Library/Fonts/',
                os.path.expanduser('~/Library/Fonts/'),
                '/System/Library/Assets/com_apple_MobileAsset_Font6/'
            ]
        else:  # Linux
            font_directories = [
                '/usr/share/fonts/',
                '/usr/local/share/fonts/',
                '/usr/X11R6/lib/X11/fonts/',
                os.path.expanduser('~/.fonts/'),
                os.path.expanduser('~/.local/share/fonts/'),
                '/system/fonts/',  # Android
            ]
        
        # 모든 폰트 디렉토리 스캔
        for font_dir in font_directories:
            if os.path.exists(font_dir):
                try:
                    self._scan_font_directory(font_dir, font_files, available_fonts)
                except Exception as e:
                    print(f"폰트 디렉토리 스캔 실패 ({font_dir}): {e}")
        
        # tkinter 시스템 폰트도 추가
        try:
            import tkinter.font as tkfont
            tk_fonts = list(tkfont.families())
            for tk_font in tk_fonts:
                if tk_font not in available_fonts:
                    available_fonts.append(tk_font)
        except:
            pass
        
        # 폰트 파일 경로 저장
        self.font_files = font_files
        
        # 중복 제거 및 정렬
        unique_fonts = []
        for font in available_fonts:
            if font not in unique_fonts:
                unique_fonts.append(font)
        
        print(f"총 {len(unique_fonts)}개의 폰트를 발견했습니다.")
        return unique_fonts
    
    def _scan_font_directory(self, directory, font_files, available_fonts):
        """폰트 디렉토리를 재귀적으로 스캔합니다."""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.ttf', '.otf', '.ttc', '.woff', '.woff2')):
                    font_path = os.path.join(root, file)
                    try:
                        # 폰트 이름 추출
                        font_name = self._extract_font_name(file)
                        if font_name and font_name not in available_fonts:
                            available_fonts.append(font_name)
                            font_files[font_name] = font_path
                            
                        # 파일명 기반 폰트명도 추가
                        file_based_name = os.path.splitext(file)[0]
                        if file_based_name and file_based_name not in available_fonts:
                            available_fonts.append(file_based_name)
                            font_files[file_based_name] = font_path
                            
                    except Exception as e:
                        print(f"폰트 파일 처리 실패 ({font_path}): {e}")
    
    def _extract_font_name(self, filename):
        """파일명에서 폰트 이름을 추출합니다."""
        # 확장자 제거
        name = os.path.splitext(filename)[0]
        
        # 일반적인 폰트 파일명 패턴 처리
        common_mappings = {
            'arial': 'Arial',
            'arialbd': 'Arial Bold',
            'ariali': 'Arial Italic',
            'arialbi': 'Arial Bold Italic',
            'times': 'Times New Roman',
            'timesbd': 'Times New Roman Bold',
            'timesi': 'Times New Roman Italic',
            'timesbi': 'Times New Roman Bold Italic',
            'cour': 'Courier New',
            'courbd': 'Courier New Bold',
            'couri': 'Courier New Italic',
            'courbi': 'Courier New Bold Italic',
            'tahoma': 'Tahoma',
            'tahomabd': 'Tahoma Bold',
            'verdana': 'Verdana',
            'verdanab': 'Verdana Bold',
            'verdanai': 'Verdana Italic',
            'verdanaz': 'Verdana Bold Italic',
            'malgun': '맑은 고딕',
            'malgunbd': '맑은 고딕 Bold',
            'gulim': '굴림',
            'batang': '바탕',
            'dotum': '돋움',
            'gungsuh': '궁서'
        }
        
        # 소문자로 변환해서 매핑 확인
        lower_name = name.lower()
        if lower_name in common_mappings:
            return common_mappings[lower_name]
        
        # 일반적인 처리: 첫 글자 대문자, 나머지 소문자
        # 단어 분리 (대문자, 숫자, 특수문자 기준)
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+|[0-9]+', name)
        if words:
            return ' '.join(word.capitalize() for word in words)
        
        return name.replace('_', ' ').replace('-', ' ').title()
        
    def get_font(self, font_name, size):
        """선택된 폰트로 PIL 폰트 객체를 생성합니다."""
        
        # "Default" 폰트인 경우 기본 폰트 사용
        if font_name == "Default":
            try:
                return ImageFont.load_default()
            except:
                return ImageFont.load_default()
        
        # 저장된 폰트 파일 경로에서 찾기
        if hasattr(self, 'font_files') and font_name in self.font_files:
            font_path = self.font_files[font_name]
            try:
                test_font = ImageFont.truetype(font_path, size)
                # 폰트 테스트
                test_img = Image.new('RGB', (100, 50), 'white')
                test_draw = ImageDraw.Draw(test_img)
                test_draw.text((10, 10), "Test", font=test_font, fill='black')
                return test_font
            except Exception as e:
                print(f"저장된 폰트 경로에서 로드 실패 ({font_path}): {e}")
        
        # tkinter 시스템 폰트 시도
        try:
            import tkinter.font as tkfont
            if font_name in tkfont.families():
                # tkinter 폰트를 PIL에서 사용하기 위해 시스템 폰트 경로 추정
                possible_paths = self._get_system_font_paths(font_name)
                for font_path in possible_paths:
                    if os.path.exists(font_path):
                        try:
                            return ImageFont.truetype(font_path, size)
                        except:
                            continue
        except:
            pass
        
        # 일반적인 폰트 경로들 시도
        font_paths = self._get_system_font_paths(font_name)
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    test_font = ImageFont.truetype(font_path, size)
                    # 폰트가 제대로 로드되는지 테스트
                    test_img = Image.new('RGB', (100, 50), 'white')
                    test_draw = ImageDraw.Draw(test_img)
                    test_draw.text((10, 10), "Test", font=test_font, fill='black')
                    return test_font
                except Exception as e:
                    print(f"폰트 로드 실패 ({font_path}): {e}")
                    continue
        
        # 모든 시도가 실패하면 기본 폰트 사용
        print(f"폰트 '{font_name}'을 찾을 수 없습니다. 기본 폰트를 사용합니다.")
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def _get_system_font_paths(self, font_name):
        """폰트 이름으로부터 가능한 시스템 폰트 경로들을 생성합니다."""
        font_paths = []
        
        if os.name == 'nt':  # Windows
            windows_fonts = {
                'Arial': ['arial.ttf', 'Arial.ttf'],
                'Arial Bold': ['arialbd.ttf', 'Arial Bold.ttf'],
                'Arial Italic': ['ariali.ttf', 'Arial Italic.ttf'],
                'Times New Roman': ['times.ttf', 'Times New Roman.ttf'],
                'Courier New': ['cour.ttf', 'Courier New.ttf'],
                '맑은 고딕': ['malgun.ttf', 'MalgunGothic.ttf'],
                'Malgun Gothic': ['malgun.ttf', 'MalgunGothic.ttf'],
                '굴림': ['gulim.ttc', 'Gulim.ttc'],
                'Gulim': ['gulim.ttc', 'Gulim.ttc'],
                'Tahoma': ['tahoma.ttf', 'Tahoma.ttf'],
                'Verdana': ['verdana.ttf', 'Verdana.ttf'],
                '바탕': ['batang.ttc', 'Batang.ttc'],
                '돋움': ['dotum.ttc', 'Dotum.ttc'],
                '궁서': ['gungsuh.ttc', 'Gungsuh.ttc']
            }
            
            base_dirs = [
                'C:/Windows/Fonts/',
                'C:/Windows/System32/Fonts/',
                os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/'),
                os.path.expanduser('~/AppData/Roaming/Microsoft/Windows/Fonts/')
            ]
            
            # 정확한 파일명이 있는 경우
            if font_name in windows_fonts:
                for filename in windows_fonts[font_name]:
                    for base_dir in base_dirs:
                        font_paths.append(os.path.join(base_dir, filename))
            
            # 일반적인 경우들 시도
            possible_names = [
                f'{font_name.lower().replace(" ", "")}.ttf',
                f'{font_name.lower()}.ttf',
                f'{font_name}.ttf',
                f'{font_name.replace(" ", "")}.ttf',
                f'{font_name.lower().replace(" ", "")}.ttc',
                f'{font_name.lower()}.ttc',
                f'{font_name}.ttc',
                f'{font_name.replace(" ", "")}.ttc'
            ]
            
            for base_dir in base_dirs:
                for name in possible_names:
                    font_paths.append(os.path.join(base_dir, name))
        
        elif hasattr(os, 'uname') and os.uname().sysname == 'Darwin':  # macOS
            base_dirs = [
                '/System/Library/Fonts/',
                '/Library/Fonts/',
                '/Network/Library/Fonts/',
                os.path.expanduser('~/Library/Fonts/')
            ]
            
            possible_names = [
                f'{font_name}.ttf',
                f'{font_name}.ttc',
                f'{font_name}.otf',
                f'{font_name.replace(" ", "")}.ttf',
                f'{font_name.replace(" ", "")}.ttc'
            ]
            
            for base_dir in base_dirs:
                for name in possible_names:
                    font_paths.append(os.path.join(base_dir, name))
        
        else:  # Linux
            base_dirs = [
                '/usr/share/fonts/',
                '/usr/local/share/fonts/',
                '/usr/X11R6/lib/X11/fonts/',
                os.path.expanduser('~/.fonts/'),
                os.path.expanduser('~/.local/share/fonts/')
            ]
            
            possible_names = [
                f'{font_name}.ttf',
                f'{font_name}.otf',
                f'{font_name.replace(" ", "")}.ttf',
                f'{font_name.replace(" ", "")}.otf',
                f'DejaVu{font_name.replace(" ", "")}.ttf',
                f'Liberation{font_name.replace(" ", "")}-Regular.ttf'
            ]
            
            for base_dir in base_dirs:
                if os.path.exists(base_dir):
                    for root, dirs, files in os.walk(base_dir):
                        for name in possible_names:
                            font_paths.append(os.path.join(root, name))
        
        return font_paths
        
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
        self.font_var = tk.StringVar(value="Default")
        font_combo = ttk.Combobox(input_frame, textvariable=self.font_var, 
                                 values=self.available_fonts, width=25, state="readonly")
        font_combo.grid(row=1, column=1, padx=5, pady=5)
        font_combo.bind('<<ComboboxSelected>>', self.on_font_changed)
        
        # 폰트 테스트 버튼 추가
        ttk.Button(input_frame, text="폰트 테스트", 
                  command=self.test_font).grid(row=1, column=2, padx=5)
        
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
        print(f"선택된 폰트: {self.selected_font}")
    
    def test_font(self):
        """선택된 폰트를 테스트합니다."""
        font_name = self.font_var.get()
        try:
            test_font = self.get_font(font_name, 30)
            
            # 테스트 이미지 생성
            img = Image.new('RGB', (400, 120), 'white')
            draw = ImageDraw.Draw(img)
            
            # 다양한 텍스트로 테스트
            test_texts = [
                "ABC abc 123",
                "한글 테스트",
                f"폰트: {font_name}"
            ]
            
            y_pos = 10
            for text in test_texts:
                try:
                    draw.text((10, y_pos), text, font=test_font, fill='black')
                    y_pos += 35
                except:
                    # 일부 폰트는 특정 문자를 지원하지 않을 수 있음
                    draw.text((10, y_pos), f"[지원하지 않는 문자: {text}]", font=test_font, fill='red')
                    y_pos += 35
            
            self.current_image = img
            self.show_preview(img)
            
            # 폰트 파일 정보 표시
            info_msg = f"폰트: '{font_name}'\n"
            if hasattr(self, 'font_files') and font_name in self.font_files:
                info_msg += f"파일: {self.font_files[font_name]}\n"
            info_msg += "폰트가 정상적으로 로드되었습니다."
            
            messagebox.showinfo("폰트 테스트", info_msg)
            
        except Exception as e:
            messagebox.showerror("폰트 오류", f"'{font_name}' 폰트를 로드할 수 없습니다.\n오류: {str(e)}")
    
    
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
            # 그려진 선이 있는지 확인
            if not self.drawing_canvas.drawn_lines:
                messagebox.showwarning("경고", "먼저 서명을 그려주세요.")
                return
            
            # 캔버스를 이미지로 변환
            img = self.drawing_canvas.get_image()
            
            if img:
                self.current_image = img
                self.show_preview(img)
                messagebox.showinfo("완료", "손글씨 서명이 저장되었습니다.\n'이미지 저장' 버튼을 눌러 파일로 저장하세요.")
            else:
                messagebox.showerror("오류", "이미지 생성에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"손글씨 서명 저장 중 오류가 발생했습니다: {str(e)}")
    
    def create_canvas_image(self):
        """캔버스를 PIL 이미지로 변환하는 대안 방법 (사용하지 않음)"""
        # 이 메서드는 더 이상 사용하지 않음
        pass
    
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