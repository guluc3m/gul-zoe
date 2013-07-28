/*
 * This file is part of Zoe Assistant - https://github.com/guluc3m/gul-zoe
 *
 * Copyright (c) 2013 David Muñoz Díaz <david@gul.es>
 *
 * This file is distributed under the MIT LICENSE
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
package es.gul.zoe;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * Bridges the Zoe server and the agents.
 * @author david
 */
public class Listener {

    private String serverHost;
    private int serverPort;

    private String agentName;
    private String host;
    private int port;
    private Conf conf;
    private Agent receiver;

    /**
     * Creates a new Zoe Listener which communicates with the Zoe server. 
     * @param agentName The name of the agent. This name must be the one configured in <tt>zoe.conf</tt>
     * like "activities" or "users". 
     * @param receiver The agent instance that will be notified of incoming messages.
     */
    public Listener(String agentName, Agent receiver) {
        this.agentName = agentName;
        this.conf = new Conf();
        serverHost = conf.getServerHost();
        serverPort = conf.getServerPort();
        host = conf.getAgentHost(this.agentName);
        if (host == null) {
            host = "localhost";
        }
        port = conf.getAgentPort(this.agentName);
        this.receiver = receiver;
    }

    /**
     * Opens a new connection to the Zoe server and waits for incoming messages. 
     * This method is blocking. You should run in in a separate thread.
     * The receiver agent will be notified of every incoming message in 
     * another separate thread. 
     * @see Agent#receive(MessageParser)
     */
    @SuppressWarnings("resource")
    public void start() {
        ServerSocket serverSocket = null;
        try {
            serverSocket = new ServerSocket(this.port);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        try {
            while (true) {
                Socket clientSocket = serverSocket.accept();
                ZoeConnection conn = new ZoeConnection(receiver, clientSocket);
                new Thread(conn).start();
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
    
    /**
     * Sends a message to the Zoe server.
     * @param builder
     */
    public void sendbus(MessageBuilder builder) {
        sendbus(builder.getMsg());
    }
    
    /**
     * Sends a message to the Zoe server.
     * @param message
     */
    public void sendbus(String message) {
        OutputStream os = null;
        try {
            @SuppressWarnings("resource")
            Socket s = new Socket(serverHost, serverPort);
            os = s.getOutputStream();
            os.write(message.getBytes());
        } catch (IOException e) {
            System.err.println("Can't connect to server: " + e);
            e.printStackTrace(System.err);
        } finally {
            if (os != null) {
                try {
                    os.close();
                } catch (IOException e) {
                    e.printStackTrace(System.err);
                }
            }
        }
    }
    
    /*
     * Dispatches an incoming connection
     */
    private class ZoeConnection implements Runnable {

        private Agent agent;
        private Socket socket;

        public ZoeConnection(Agent agent, Socket socket) {
            this.agent = agent;
            this.socket = socket;
        }

        @Override
        public void run() {
            byte[] message = null;
            
            try {
                InputStream is = this.socket.getInputStream();
                ByteArrayOutputStream os = new ByteArrayOutputStream();
                byte[] buf = new byte[1024];
                int read;
                while ((read = is.read(buf)) > 0) {
                    os.write(buf, 0, read);
                }
                message = os.toByteArray();
            } catch (IOException e) {
                System.out.println("Can't read from socket: " + e);
                e.printStackTrace();
                return;
            } finally {
                try {
                    socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            
            MessageParser parser = null;
            parser = new MessageParser(message) ;
            
            try {
                agent.receive(parser);
            } catch (Exception e) {
                System.err.println("Message crashed: " + e);
                e.printStackTrace(System.err);
            }
        }
    }
}
