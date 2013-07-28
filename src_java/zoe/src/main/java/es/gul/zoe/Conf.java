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

import java.io.File;
import java.io.IOException;

import org.ini4j.Wini;

public class Conf {

    private String ZOE_HOME;
    private Wini zoeConf;

    public Conf() {
        ZOE_HOME = getEnvorinment("ZOE_HOME");
        File f = new File(ZOE_HOME, "src/zoe.conf");
        if (f == null || !f.exists()) {
            throw new RuntimeException("cone.conf not found in $ZOE_HOME");
        }
        try {
            zoeConf = new Wini(f);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private String getEnvorinment(String name) {
        String s = System.getenv(name);
        if (s == null || s.equals("")) {
            throw new RuntimeException("ZOE not correctly configured, please set environment variable " + name);
        }       
        return s;
    }
    
    public String getServerHost() {
        return getEnvorinment("ZOE_SERVER_HOST");
    }
    
    public int getServerPort() {
        return Integer.parseInt(getEnvorinment("ZOE_SERVER_PORT"));
    }
    
    public int getAgentPort(String agentName) {
        String section = "agent " + agentName;
        return zoeConf.get(section, "port", int.class);
    }

    public String getAgentHost(String agentName) {		
        String section = "agent " + agentName;
        return zoeConf.get(section, "host", String.class);
    }
}
