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
package org.voiser.zoe;

import java.util.LinkedHashMap;
import java.util.Map;

import es.gul.zoe.MessageBuilder;
import es.gul.zoe.MessageParser;
import es.gul.zoe.SimpleAgent;
import es.gul.zoe.Validate;
import es.gul.zoe.ValidationException;

/**
 * An example agent. This example uses SimpleAgent as the base class
 * which adds some util methods to communicate with the Zoe Server.
 * @author david
 */
public class EchoAgent extends SimpleAgent {

    public EchoAgent() {
        super("echo");
    }
    
    @Override
    public void receive(MessageParser original) throws Exception {

        // log the incoming message
        System.out.println("Message received: " + original.toString());
        
        // extract message parameters
        String origin = original.get("src");
        String msg = original.get("msg");
        
        // check parameters
        Validate.string(origin);
        Validate.string(msg);
        
        // Generate the new message from a map
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("src", "echo");
        map.put("dst", origin);
        map.put("msg", msg);
        
        // Send the new message
        sendbus(new MessageBuilder(map, original));
    }
}
