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

import java.util.List;
import java.util.Map;
import java.util.UUID;

public class MessageBuilder {

    private String msg;

    public MessageBuilder(Map<String, Object> map) {
        this(map, null);
    }

    @SuppressWarnings("unchecked")
    public MessageBuilder(Map<String, Object> map, MessageParser original) {
        if (original != null) {
            String originalCid = original.get("_cid");
            if (originalCid != null) {
                map.put("_cid", originalCid);
            }
        }
        if (!map.containsKey("_cid")) {
            map.put("_cid", UUID.randomUUID());
        }
        StringBuilder sb = new StringBuilder();
        for (String key : map.keySet()) {
            Object value = map.get(key);
            if (value == null) continue;
            if (value instanceof List){
                for (String v : (List<String>)value) {
                    sb.append(key).append("=").append(v).append("&");					
                }
            } else {
                sb.append(key).append("=").append(value).append("&");
            }
        }
        msg = sb.toString();
    }

    public String getMsg() {
        return msg;
    }
    
    @Override
    public String toString() {
        return getMsg();
    }
}
