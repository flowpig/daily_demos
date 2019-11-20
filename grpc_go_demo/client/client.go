package main

import (
    "log"
    "os"
    "golang.org/x/net/context"
    "google.golang.org/grpc"
    pb "../example"
)

const (
    address     = "127.0.0.1:19999"
    defaultName = "world"
)

func main() {
    // Set up a connection to the server.
    conn, err := grpc.Dial(address, grpc.WithInsecure())
    if err != nil {
        log.Fatalf("did not connect: %v", err)
    }
    defer conn.Close()
    c := pb.NewGreeterClient(conn)

    // Contact the server and print out its response.
    name := defaultName
    if len(os.Args) > 1 {
        name = os.Args[1]
    }
    r, err := c.SayHello(context.Background(), &pb.HelloRequest{Name: name, Message: "Hello!"})
    if err != nil {
        log.Fatalf("could not greet: %v", err)
    }
    log.Printf("####### get server Greeting response: %s", r.Message)
}
