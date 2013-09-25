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

public class AgentLoader {
    
    private static class AgentLauncher implements Runnable {

        private Class<? extends Agent> k;
        
        public AgentLauncher(Class<? extends Agent> k) {
            this.k = k;
        }

        @Override
        public void run() {
            try {
                k.newInstance();
            } catch (InstantiationException | IllegalAccessException e) {
                System.out.println("Can't start agent + " + k);
                e.printStackTrace(System.err);
            }
        }
    }
    
    public static void main(String... args) {
        for (String agent : args) {
            try {
                final Class<? extends Agent> k = Class.forName(agent).asSubclass(Agent.class);
                System.out.println("Starting agent " + agent);
                AgentLauncher launcher = new AgentLauncher(k);
                new Thread(launcher).start();
            } catch (ClassNotFoundException e) {
                System.err.println("Can't find agent class " + agent);
            }
        }
    }
}
