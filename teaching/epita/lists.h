#ifndef LIST_H
#define LIST_H

/**
 * struct list - a list element
 *
 * @data: data stored inside the list node, not owned by the list
 * @next: pointer to the next element
 */
struct list {
	void *data;
	struct list *next;
};

/**
 * new_list() - Create a list
 *
 * Returns:
 * a newly created list
 */
struct list *new_list(void);

/**
 * list_insert_head() - Insert an element in a list
 * @l: list
 * @data: pointer to the data
 *
 * Returns:
 * pointer to the list or NULL on error
 */
struct list *list_insert_head(struct list *l, void *data);

/**
 * list_remove_head() - Remove the first element of a list
 * @l: list
 * @data: pointer to the data stored in the removed node
 *
 * The data stored in the removed element is return in the @data parameter.
 *
 * Returns:
 * pointer to the list
 */
struct list *list_remove_head(struct list *l, void **data);

/**
 * list_iter() - execute a function for all elements of the list
 * @l: list
 * @func: function called on all the elements of the list
 * @arg: custom data passed to @func
 *
 */
void list_iter(struct list *l, void (*func)(struct list *, void *), void *arg);

/**
 * list_delete() - delete the list
 * @l: list
 * @dtor: function used to destroy all the elements stored inside @l
 * @arg: custom data passed to @dtor
 *
 * This function take the destructor for all the data stored inside the list.
 * First parameter of @dtor is the list data, and the other one is the @arg
 * parameter.
 */
void list_delete(struct list *l, void (*dtor)(void *, void *), void *arg);

/**
 * list_find() - Find the first element matching a predicate in a list
 * @l: list
 * @predicate: boolean function used to find a list element
 * @arg: custom data passed to @predicate
 *
 * Returns:
 * first list node that match @predicate or NULL if no element match the
 * predicate
 */
struct list *list_find(struct list *l, int (*predicate)(void *, void *), void *arg);


#endif /* LIST_H */
