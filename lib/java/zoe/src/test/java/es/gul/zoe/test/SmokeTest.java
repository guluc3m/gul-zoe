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
package es.gul.zoe.test;

import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.junit.Test;

import static org.junit.Assert.*;
import es.gul.zoe.Agent;
import es.gul.zoe.Conf;
import es.gul.zoe.Listener;
import es.gul.zoe.MessageBuilder;
import es.gul.zoe.MessageParser;

public class SmokeTest {

    @Test
    public void canReadConf() throws Exception {
        Conf conf = new Conf();
        assertTrue (conf.getAgentPort("activities") > 30000);
        assertNotNull (conf.getServerHost());
        assertEquals(30000, conf.getServerPort());
    }

    @Test
    public void messageParser() throws Exception {
        byte[] message = "a=b&c=d&e=f&e=g".getBytes();
        MessageParser p = new MessageParser(message);
        assertEquals("b", p.get("a"));
        assertEquals("d", p.get("c"));
        assertNull(p.get("x"));
        List<String> list = p.list("e");
        assertNotNull(list);
        assertEquals(2, list.size());
    }
    
    @Test
    public void messageBuilder() throws Exception {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("a", "b");
        map.put("c", "d");
        List<String> l = new LinkedList<>();
        l.add("f");
        l.add("g");
        map.put("e", l);
        String msg = new MessageBuilder(map).getMsg();

        MessageParser p = new MessageParser(msg.getBytes());
        assertEquals("b", p.get("a"));
        assertEquals("d", p.get("c"));
        assertNull(p.get("x"));
        List<String> list = p.list("e");
        assertNotNull(list);
        assertEquals(2, list.size());
    }
    
    @Test
    public void messageBuildsWithCid() throws Exception {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("a", "b");
        map.put("c", "d");
        String msg = new MessageBuilder(map).getMsg();
        MessageParser p = new MessageParser(msg.getBytes());
        assertNotNull(p.get("_cid"));
    }
}
