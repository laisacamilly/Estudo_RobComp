import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import ReliabilityPolicy, QoSProfile
# Importar a classe da acao do arquivo, como por exemplo

# Imports QUE COLOQUEI: --------
from robcomp_util.odom import Odom
from robcomp_util.laser import Laser
#from .girar import Girar
from robcomp_util.andar import Andar

#Import do publisher:
from robcomp_interfaces import GameStatus

class Jogador(Node, Laser, Odom, Andar): # Nome da classe Jogador e adicionei heranças.

    def __init__(self):
        super().__init__('jogador_node') # Mudei o nome do nó.
        # Outra Herança que você queira fazer - COLOQUEI -:
        Laser.__init__(self)
        Odom.__init__(self)
        Andar.__init__(self)

        rclpy.spin_once(self) # Roda pelo menos uma vez para pegar os valores

        # Cria o nó da Acao, INICIA ELE:
        self.jogador_node = Jogador()

        # MAQUINA DE ESTADOS -------------------------------------
        self.robot_state = 'andar' #começa com status in progress.
        self.state_machine = {
            'andar': self.andar,
            'parar': self.parar, 
            'girar': self.girar,
            'esperar': self.esperar
        }

        # ----------------------------------------------------------

        # Inicialização de variáveis
        self.twist = Twist()
        self.andar = Andar()

        self.vel = 0.1 #velocidade q ele anda
        
        # Subscribers - COLOQUE AQUI OS SUB ---------------------------------
        self.pub_sub = self.create_subscription(
            GameStatus,
            '/young_hee',
            self.pub_callback, #Executada a cada mensagem recebida.
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        #Def pub callback (que é a mesnagem texto q ele fala.)
        
        # ---------------------------------------------------------------------


        # Publishers - COLOQUE AQUI OS PUB -------------------------- :
        self.cmd_vel_pub = self.create_publisher(GameStatus, '/young_hee', 10)

        # PUBLICANDO NÓ:
        msg = GameStatus() #Cria uma mensagem do tipo GameStatus()
        # Ver pelo comando interface (no terminal)!

        msg.status ='READY'
        
        #Horario atual:
        current_time = self.get_clock().now().to_msg()
        current_time = float(current_time.sec) + float(current_time.nanosec) / (10**9)
        msg.start_time = current_time #Recebe o horario atual.

        msg.player_name = "Laisa"

        self.vel_pub.publish(msg) # Publica a mensagem.
        # ---------------------------------------------------------------------

        ## Por fim, inicialize o timer
        self.timer = self.create_timer(0.1, self.control)
    

    # AQUI criar os METODOS que estão na maquina de estados de acordo com o enunciado: -------------------------
    def andar(self, msg):
        dist = float(min(self.front))

        if (msg.current_word == "ba") or (msg.current_word == "ta") or (msg.current_word == "ti"):
            self.twist.linear.x = self.vel #anda
            
            #Parede:
            if dist <= 1: #distancia do robo e a parede - 1m.
                self.robot_state = 'esperar'
    
    def parar (self, msg):
        if (msg.current_word == 3):
            self.robot_state = 'esperar'

    def girar (self, msg):
        dist = float(min(self.front))

        if dist < 1:
            self.robot_state = 'girar'
        

    def esperar(self):
        self.twist = Twist()

# ---------------------------------------------------------

    def control(self): # Controla a máquina de estados - eh chamado pelo timer
        print(f'Estado Atual: {self.robot_state}')
        self.state_machine[self.robot_state]() # Chama o método do estado atual 
        self.cmd_vel_pub.publish(self.twist) # Publica a velocidade
 
def main(args=None):
    rclpy.init(args=args) # Inicia o ROS2
    ros_node = Jogador() # Cria o nó

    while not ros_node.robot_state == 'done': # Enquanto o robô não estiver parado
        rclpy.spin_once(ros_node) # Processa os callbacks e o timer

    ros_node.destroy_node() # Destroi o nó
    rclpy.shutdown() # Encerra o ROS2
