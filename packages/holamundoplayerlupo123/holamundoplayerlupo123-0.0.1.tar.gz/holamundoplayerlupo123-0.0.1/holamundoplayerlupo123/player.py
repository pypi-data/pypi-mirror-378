"""
Esta es el modulo que incluye la clase
de reproductor de musica
"""

# antes de definir el constructor y los metodos ponemos los doctstring


class Player:
    """
    Esta clase crea un reproductor
    de musica
    """
# para documentar metodo hacemos lo mismo de poner las triples comillas dobles
# si es de multiples lineas el doctring los ponemos separados  como en la clase player, sino todo en una linea
# la nomenclatura de Parameters Returns escribirla tal cual es norma para que los docstring queden ok

    def play(self, song: str) -> int:
        """
        Reproduce la cancion que recibio como parametro


        Parameters :
        song (str) : Este es un string con el path de la cancion

        Returns :
        int : devuelve 1 si reproduce con exito, en caso de fracaso devuelve un 0
        """
        print(f"reproducinedo cancion {song}")

    def stop(self):
        print("stopping")
