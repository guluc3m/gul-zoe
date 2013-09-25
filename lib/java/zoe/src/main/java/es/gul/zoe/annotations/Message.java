package es.gul.zoe.annotations;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * <p>
 * Indicates the method that should be executed when 
 * a message with the given tags arrives. 
 * If no tags are specified, the method will be
 * invoked when a message with no tags arrives.
 * If any tag is specified, the method will be invoked when
 * a message that contains at least these tags (and possibly more) arrives.
 * </p>
 * @author dmunoz
 *
 */
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD})
public @interface Message {
	String[] tags() default "";
}
