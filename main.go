package main

import (
	"crypto/tls"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"

	ppmapi "github.com/GandhiNN/ppmapi/api"
)

func main() {

	// Start Time
	//timenow := time.Now()

	// Create a HTTP Transport Object
	// and then create a *http.Client object afterward
	tr := &http.Transport{
		MaxIdleConns:       30,
		IdleConnTimeout:    30 * time.Second,
		DisableCompression: true,
		// Handle insecure key/x509 cert error and,
		// resolve the "connection reset by peer" by capping TLS at version 1.1 and retrying
		// SEE: http://www.debug.is/2017/11/01/http-tls-handling-go-http-client/
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true, MaxVersion: tls.VersionTLS11},
	}
	client := &http.Client{Transport: tr}

	// Accept script arguments
	startDate, endDate, nodeIP, nodeName, resourceName := CLIFlags()

	// Create API object
	api := ppmapi.API{
		Client:          client,
		URI:             "cbtcnb03-vppm.xl.id:4440",
		NodeIP:          nodeIP,
		NodeName:        nodeName,
		IntervalTypeKey: "HOUR",
		DurationSelect:  "",
		StartDate:       startDate,
		EndDate:         endDate,
		User:            "psi_gandhi",
		Password:        "Ps1ps2ps3!",
	}

	// Set to working directory
	path, err := os.Executable()
	if err != nil {
		log.Fatal("error reading path: ", err)
	}
	dir := filepath.Dir(path)

	// Call the REST resources
	callResource := func(resource, outputfile string, api ppmapi.API) {
		url, err := ppmapi.URLBuilder(resource, api)
		if err != nil {
			log.Fatal("error reading config file: ", err)
		}
		var (
			respBody []byte
			retries  = 3
		)
		for retries > 0 {
			respBody, err = api.GetCSV(url)
			if err != nil {
				log.Fatal(err)
				log.Print("connection reset by peer, retrying...")
				retries--
			} else {
				break
			}
		}
		/*
			respBody, err := api.GetCSV(url)
		*/
		ppmapi.WriteCSV(outputfile, respBody)
	}
	resource := FileNameGenerator(resourceName, api)
	callResource(resourceName, dir+"/"+resource, api)
}

// CLIFlags Handle script arguments
func CLIFlags() (string, string, string, string, string) {
	// Flag pointer
	startDatePtr := flag.String("start", "2019-01-01", "Start Date of Data => YYYY-MM-DD: string")
	endDatePtr := flag.String("end", "2019-01-31", "End Date of Data => YYYY-MM-DD: string")
	nodeIPPtr := flag.String("node", "127.0.0.1", "IP Address of StarOS node")
	nodeNamePtr := flag.String("nodename", "All-Node", "StarOS Node Name")
	resourceNamePtr := flag.String("resource", "CPU_Load", "KPI Resource Name")

	// Parse the Flag
	flag.Parse()

	return *startDatePtr, *endDatePtr, *nodeIPPtr, *nodeNamePtr, *resourceNamePtr
}

// FileNameGenerator generates the output filename of the API call result
func FileNameGenerator(resource string, api ppmapi.API) string {
	return fmt.Sprintf("%s-%s-%s-%s.csv", api.NodeName, resource, api.StartDate, api.EndDate)
}
