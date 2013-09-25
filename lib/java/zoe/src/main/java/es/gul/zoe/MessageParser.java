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

import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class MessageParser {

    private String origMsg;
    private Map<String, List<String>> map;

    public MessageParser(String msg) {
    	this(msg.getBytes());
	}
    
    public MessageParser(byte[] message) {
        origMsg = new String(message);
        map = new LinkedHashMap<>();
        String s = new String(message);
        String[] pairs = s.split("&");
        for (String pair : pairs) {
            String[] parts = pair.split("=");
            if (parts.length == 2) {
                String key = parts[0];
                String value = parts[1];
                List<String> current = map.get(key);
                if (current == null) {
                    current = new LinkedList<>();
                    map.put(key, current);
                }
                current.add(value);
            }
        }
    }

    public String get(String key) {
        List<String> values = map.get(key);
        if (values == null) 
            return null;
        return values.get(0);
    }

    public List<String> list(String key) {
        return map.get(key);
    }

    public List<String> tags() {
        return list("tag");
    }
    
    public Set<String> keys() {
        return map.keySet();
    }
    
    @Override
    public String toString() {
        return origMsg;
    }
}    
