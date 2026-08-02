//OJO: Este archivo no pertenece a ningún paquete (package)

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Arrays;
/**
 * Programa para calcular la cantidad y suma de numeros pares en una lista de numeros
 * @author Jorge Duitama
 */
public class ProblemaP0 {

	public static void main(String[] args) throws Exception {
		ProblemaP0 instancia = new ProblemaP0();
		try ( 
			InputStreamReader is= new InputStreamReader(System.in);
			BufferedReader br = new BufferedReader(is);
		) { 
			String line = br.readLine();
			int casos = Integer.parseInt(line);
			line = br.readLine();
			for(int i=0;i<casos && line!=null && line.length()>0;i++) {
				final String [] dataStr = line.split(" ");
				final int[] numeros = Arrays.stream(dataStr).mapToInt(f->Integer.parseInt(f)).toArray();
				int [] respuestas = instancia.procesarNumeros(numeros);
				System.out.println(respuestas[0]+" "+respuestas[1]);
				line = br.readLine();
			}
		}
	}
	/**
	 * Calcula la cantidad de pares y la suma de pares de una lista de numeros
	 * @param numeros a procesar 
	 * @return int [] arreglo de dos posiciones. La primera tiene la cantidad de numeros pares
	 * y la segunda la suma de los numeros 
	 */
	public int [] procesarNumeros(int[] numeros) {
		int [] respuestas = {0,0};
		for(int i=0;i<numeros.length;i++) {
			if(numeros[i]%2==0) {
				respuestas[0]++;
				respuestas[1]+=numeros[i];
			}
		}
		return respuestas;
	}

}
