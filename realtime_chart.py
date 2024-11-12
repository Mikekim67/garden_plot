import sys
import serial
import matplotlib.pyplot as plt
import numpy as np

# virtualenv 설치하고 모듈 불러오기
# python realtime_chart.py <포트번호> 460800
# 해당 위치에서 & .\.venv\Scripts\activate

class realtime_chart: # 사용할 class
    def __init__(self): # 생성자? 정의, 사용하는 변수
        self.fig, self.ax = plt.subplots() 
        # 그래프 두개이상 보여줄때
        # fig : 전체 그림을 담는 figure 객체
        # ax : 개별 그래프(축)를 담는 axews 객체

        self.fig.show() # pyplot으로 GUI, 그래프 보여주기
        self.ch_num = 0 #채널갯수
        self.width = 50 # plot창 사이즈 초기값 5000
        self.redraw = False
        self.data = np.empty((0, self.ch_num), dtype=int) 
        # np.empty((0, self.ch_num), dtype=int) 비어있는 배열생성, (row,col)=(0, self.ch_num), 자료형 int

        self.x = np.empty((0), dtype=int)
        self.seq_num = 0
    
    def add_plot_data(self, value_list): #멤버함수?
        if np.size(value_list) != self.ch_num: # self.ch_num 초기값은 0이므로 아래 코드를 실행함
            # value_list 배열 크기가 채널갯수와 다를때, value list는 측정한 데이터, 2채널인 경우 A,B 형식

            self.ch_num = np.size(value_list) # value_list 배열 크기만큼 ch_num 설정
            self.data = np.empty((0, self.ch_num), dtype=int) # 비어있는 np배열 data는 [0][채널 수] 크기 , int자료형
            self.x = np.empty((0), dtype=int) # x는 비어있는 1차원 행렬
            self.seq_num = 0
            self.redraw = True

        self.data = np.vstack((self.data, value_list))  
        # 이전에 만들었던 [0][채널 수] 크기만큼의 배열 self.data 아래행에 value_list행 추가하기 (stack함)
        self.x = np.append(self.x, self.seq_num) # x(축)에 self.seq_num만큼 더함
        # 그러므로 plot한다면 self.x위치에 self.data만큼을 가지는 2차원 데이터를 plot

        self.seq_num += 1 # self.seq_num을 1씩 증가==다음번 plot될 x위치 

    def update(self):
        if plt.fignum_exists(self.fig.number) is not True: # figure 창이 없는경우, false 반환
            
            return False # 이를통해 figure가 사라진 상태에서 발생할 수 있는 오류 방지
        
        trim_cnt = np.size(self.x) - self.width # trim_counter = x크기 - self.width, -5000에서 시작
        if trim_cnt > 0: #trim_cnt > 0될때, x크기가 5000 넘는경우
            self.x = self.x[trim_cnt:] # 새로운 x필드 만들기
            self.data = self.data[trim_cnt:,:] # data도 새로운 필드로

        if self.redraw is True: # self.redraw가 활성화 된 경우, 다시그리기
            self.ax.cla()
            self.ax.plot(self.x, self.data, linewidth=0.5)
            self.ax.set_title("plot of sensor data")
            self.ax.set_xlabel("number of samples")
            self.ax.set_ylabel("adc code")
            self.ax.legend([f"ch{ch}" for ch in range(self.ch_num)], loc='upper right', fontsize = 10)
            self.redraw = False # 다시 그리고 초기값 False로
        else:
            for ch in range(self.ch_num): # self.redraw 비활성화인 경우, 그래프 그리기
                self.ax.lines[ch].set_data(self.x, self.data[:,ch]) # x축, self.data에서 해당하는 ch

        self.ax.relim() #plot된 x y데이터에 맞추어 한계치 재설정 (자동 축 스케일에서 사용할) 
        self.ax.autoscale_view() 
        # 데이터에 맞추어 자동으로 축 스케일, 초기 : self.ax.autoscale_view() 
        plt.pause(0.01) # 업데이트까지 대기시간
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python realtime_chart.py <port> <baudrate>")
        sys.exit(1)


    port = sys.argv[1]
    baudrate = int(sys.argv[2])
    try:
        comm = serial.Serial(port, baudrate) # (port, baudrate)는 입력받은 값
        comm.readline() # 입력받은 포트와 속도로 읽기
    except serial.SerialException as e: # 예외상황 발생하면 exit() 
        print(f"{e}")
        sys.exit(1)

    chart = realtime_chart()

    try:
        while True: # 무한루프
            while comm.in_waiting:
                try:
                    line = comm.readline().decode()
                    value_list = np.array([int(elem) for elem in line.split(',')]) 
                    # line 문자열을 , 로 구분하고 정수로 나타낸 다음 numpy 배열로

                    chart.add_plot_data(value_list) 
                    # realtime_chart().add_plot_data(value_list) 이전에서 만들었던 배열을 plot
                except:
                    continue

            if chart.update() is False:
                break

    except KeyboardInterrupt:
        comm.close()