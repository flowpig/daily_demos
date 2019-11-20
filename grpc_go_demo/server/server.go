package main

import (
    "log"
    "net"
    "golang.org/x/net/context"
    "google.golang.org/grpc"
    pb "../example"
    "google.golang.org/grpc/reflection"
    "fmt"
)

const (
    port = "127.0.0.1:19999"
)

// server is used to implement example.GreeterServer.
type server struct{}

// SayHello implements example.GreeterServer
func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
    fmt.Println("######### get client request name :"+in.Name)
    fmt.Println("######### get client request message :"+in.Message)
    return &pb.HelloReply{Message: "Hello " + in.Name + in.Message}, nil
}

func main() {
    lis, err := net.Listen("tcp", port)
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }
    s := grpc.NewServer()
    pb.RegisterGreeterServer(s, &server{})
    // Register reflection service on gRPC server.
    reflection.Register(s)
    if err := s.Serve(lis); err != nil {
        log.Fatalf("failed to serve: %v", err)
    }
}
