package main

import (
	"os"
	"fmt"
)

func main() {
	var (
		OutputFile = "./1.txt"
	)
	file, err := os.OpenFile(OutputFile, os.O_RDWR|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		fmt.Println("Failed to open the file", err.Error())
		return
	}
	defer file.Close()
	file.WriteString("12345")
	file.WriteString("\n678910")
}
  
