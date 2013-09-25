package es.gul.zoe.annotations;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * <p>
 * Indicates that the incoming message must contain only 
 * tags declared in the @Message annotation.
 * </p>
 * <p>
 * This annotation prevents ambiguity when there is not a 1-to-1
 * relationship between message and methods. Suppose, as an example, 
 * a method annotated with:
 * <pre>@Message(tags = {A, B})</pre>
 * and another method annotated with:
 * <pre>@Message(tags = {A, B, C})</pre>
 * In this case, an arriving message like:
 * <pre>tag=A & tag=B</pre>
 * can not be dispatched unambiguously. In this case, the methods should be 
 * annotated with @Strict.
 * </p>
 * @author dmunoz
 * @see @Message
 *
 */
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD})
public @interface Strict {

}
