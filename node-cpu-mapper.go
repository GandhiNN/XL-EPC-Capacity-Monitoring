// node-cpu-mapper converts a CSV export
// of GGSN card-function mapping into JSON format
// to be consumed by our Python post-processing tool
package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

// CardMap is the container object for our map of cards
type CardMap struct {
	NodeName  string
	CF        []int
	SFStandby []int
	Demux     []int
}

func main() {

	// Primitive for accepting command-line args
	if len(os.Args) != 2 {
		fmt.Println("Usage:", os.Args[0], "FILENAME")
		return
	}
	filename := os.Args[1]

	// Load the csv file
	csvFile, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}
	defer csvFile.Close()

	reader := csv.NewReader(csvFile)
	reader.FieldsPerRecord = -1

	csvData, err := reader.ReadAll()
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	var cardmap CardMap
	var cardmaps []CardMap

	for i, line := range csvData {
		if i == 0 {
			// skip header line
			continue
		}
		cardmap.NodeName = line[0]
		cardmap.CF, err = sliceAtoi(line[1])
		if err != nil {
			log.Fatal(err)
			os.Exit(1)
		}
		cardmap.SFStandby, err = sliceAtoi(line[2])
		if err != nil {
			log.Fatal(err)
			os.Exit(1)
		}
		cardmap.Demux, err = sliceAtoi(line[3])
		if err != nil {
			log.Fatal(err)
			os.Exit(1)
		}
		cardmaps = append(cardmaps, cardmap)
	}

	// Convert to JSON with indent of 4 spaces
	jsonData, err := json.MarshalIndent(cardmaps, "", "    ")
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	// Save to file
	jsonFile, err := os.Create(strings.Trim(filename, ".csv") + ".json")
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}
	defer jsonFile.Close()

	jsonFile.Write(jsonData)
	jsonFile.Close()
}

func sliceAtoi(sa string) ([]int, error) {
	// TODO: [a;b] into []string
	sa = strings.Replace(sa, "[", "", -1)
	sa = strings.Replace(sa, "]", "", -1)
	saSlice := strings.Split(sa, ";")
	si := make([]int, 0, len(sa))
	for _, a := range saSlice {
		i, err := strconv.Atoi(a)
		if err != nil {
			return si, err
		}
		si = append(si, i)
	}
	return si, nil
}
